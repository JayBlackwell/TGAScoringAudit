#!/usr/bin/env python3
"""Flask web application for TGA Scoring Audit."""

import os
import csv
import tempfile
from datetime import datetime
from typing import List, Optional, Dict, Any
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from flask_session import Session

from tga_scoring_audit.config import Config
from tga_scoring_audit.api.golf_genius import GolfGeniusAPI
from tga_scoring_audit.api import AuthenticationError
from tga_scoring_audit.models.season import Season
from tga_scoring_audit.models.event import Event
from tga_scoring_audit.models.round import Round
from tga_scoring_audit.analysis.scoring import ScoringAnalyzer
from tga_scoring_audit.utils.date_helpers import validate_date_range, is_date_in_range, format_date_for_display

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
Session(app)

# Initialize components
config = Config()
analyzer = ScoringAnalyzer()


@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')


@app.route('/api_key', methods=['GET', 'POST'])
def api_key_setup():
    """API key input and validation."""
    if request.method == 'POST':
        api_key = request.form.get('api_key', '').strip()
        
        if not api_key:
            flash('API key is required', 'error')
            return render_template('api_key.html')
        
        try:
            # Test API connection
            config.set_api_key(api_key)
            api = GolfGeniusAPI(config)
            
            if not api.test_connection():
                flash('Failed to connect to Golf Genius API. Please check your API key.', 'error')
                return render_template('api_key.html')
            
            # Store in session
            session['api_key'] = api_key
            flash('Successfully connected to Golf Genius API!', 'success')
            return redirect(url_for('season_selection'))
            
        except AuthenticationError as e:
            flash(f'Authentication failed: {str(e)}', 'error')
            return render_template('api_key.html')
        except Exception as e:
            flash(f'Connection error: {str(e)}', 'error')
            return render_template('api_key.html')
    
    return render_template('api_key.html')


@app.route('/seasons')
def season_selection():
    """Season selection page."""
    if 'api_key' not in session:
        return redirect(url_for('api_key_setup'))
    
    try:
        config.set_api_key(session['api_key'])
        api = GolfGeniusAPI(config)
        seasons_data = api.get_seasons()
        seasons = [Season.from_api_response(data) for data in seasons_data]
        
        return render_template('seasons.html', seasons=seasons)
        
    except Exception as e:
        flash(f'Error fetching seasons: {str(e)}', 'error')
        return redirect(url_for('api_key_setup'))


@app.route('/date_range', methods=['GET', 'POST'])
def date_range_selection():
    """Date range selection page."""
    if 'api_key' not in session:
        return redirect(url_for('api_key_setup'))
    
    season_id = request.args.get('season_id') or request.form.get('season_id')
    season_name = request.args.get('season_name') or request.form.get('season_name')
    
    if not season_id:
        flash('Please select a season first', 'error')
        return redirect(url_for('season_selection'))
    
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        
        try:
            # Validate dates
            start_dt, end_dt = validate_date_range(start_date, end_date)
            
            # Store in session
            session['season_id'] = season_id
            session['season_name'] = season_name
            session['start_date'] = start_date
            session['end_date'] = end_date
            
            return redirect(url_for('run_analysis'))
            
        except ValueError as e:
            flash(f'Invalid date range: {str(e)}', 'error')
    
    return render_template('date_range.html', season_name=season_name, season_id=season_id)


@app.route('/analysis')
def run_analysis():
    """Run the scoring analysis."""
    if 'api_key' not in session or 'season_id' not in session:
        return redirect(url_for('api_key_setup'))
    
    return render_template('analysis.html')


@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint to run the analysis."""
    if 'api_key' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        # Setup API
        config.set_api_key(session['api_key'])
        api = GolfGeniusAPI(config)
        
        season_id = session['season_id']
        start_date = session['start_date']
        end_date = session['end_date']
        
        # Parse dates
        start_dt, end_dt = validate_date_range(start_date, end_date)
        
        # Fetch events
        events_data = api.get_all_events(season_id)
        events = [Event.from_api_response(data) for data in events_data]
        
        # Collect rounds
        all_rounds = []
        for event in events:
            try:
                rounds_data = api.get_rounds(event.id)
                rounds = [Round.from_api_response(data, event.id) for data in rounds_data]
                all_rounds.extend(rounds)
            except Exception as e:
                continue
        
        # Filter by date range
        filtered_rounds = [r for r in all_rounds if is_date_in_range(r.date, start_dt, end_dt)]
        
        # Analyze scoring
        flagged_rounds = []
        for round_obj in filtered_rounds:
            try:
                tee_sheet_data = api.get_tee_sheet(round_obj.event_id, round_obj.id)
                is_flagged, reason = analyzer.analyze_round_scoring(tee_sheet_data)
                
                if is_flagged:
                    round_obj.flag(reason)
                    flagged_rounds.append(round_obj)
                    
            except Exception as e:
                round_obj.flag(f"Unable to retrieve scoring data: {str(e)}")
                flagged_rounds.append(round_obj)
                continue
        
        # Store results in session
        results_data = []
        for round_obj in flagged_rounds:
            results_data.append({
                'event_id': round_obj.event_id,
                'round_id': round_obj.id,
                'date': format_date_for_display(round_obj.date),
                'name': round_obj.name,
                'reason': round_obj.flag_reason,
                'scorecard_url': f"https://www.golfgenius.com/leagues/{round_obj.event_id}/rounds/{round_obj.id}/scorecards"
            })
        
        session['results'] = results_data
        
        return jsonify({
            'success': True,
            'message': f'Analysis complete! Found {len(flagged_rounds)} flagged rounds',
            'flagged_count': len(flagged_rounds),
            'total_rounds': len(filtered_rounds),
            'redirect': url_for('results')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/results')
def results():
    """Display analysis results."""
    if 'results' not in session:
        flash('No analysis results found. Please run an analysis first.', 'error')
        return redirect(url_for('index'))
    
    results_data = session['results']
    return render_template('results.html', results=results_data)


@app.route('/download_csv')
def download_csv():
    """Download results as CSV file."""
    if 'results' not in session:
        flash('No analysis results found.', 'error')
        return redirect(url_for('index'))
    
    results_data = session['results']
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', newline='')
    
    try:
        writer = csv.writer(temp_file)
        writer.writerow(['Event ID', 'Round ID', 'Date', 'Round Name', 'Issue', 'Scorecard URL'])
        
        for result in results_data:
            writer.writerow([
                result['event_id'],
                result['round_id'],
                result['date'],
                result['name'],
                result['reason'],
                result['scorecard_url']
            ])
        
        temp_file.close()
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tga_scoring_audit_{timestamp}.csv"
        
        return send_file(temp_file.name, as_attachment=True, download_name=filename, mimetype='text/csv')
        
    except Exception as e:
        flash(f'Error generating CSV: {str(e)}', 'error')
        return redirect(url_for('results'))
    finally:
        # Clean up temp file after sending
        try:
            os.unlink(temp_file.name)
        except:
            pass


@app.route('/clear_session')
def clear_session():
    """Clear session data and start over."""
    session.clear()
    flash('Session cleared. Starting fresh.', 'info')
    return redirect(url_for('index'))


if __name__ == '__main__':
    # For development only - use a proper WSGI server in production
    app.run(debug=True, host='0.0.0.0', port=5000)