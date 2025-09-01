##Standard Workflow
1. First think through the problem, read the codebase for relevant files, and write a plan to tasks/todo.md.
2. The plan should have a list of todo items that you can check off as you complete them
3. Before you begin working, check in with me and I will verify the plan.
4. Then, begin working on the todo items, marking them as complete as you go.
5. Please every step of the way just give me a high level explanation of what changes you made
6. Make every task and code change you do as simple as possible. We want to avoid making any massive or complex changes. Every change should impact as little code as possible. Everything is about simplicity.
7. Finally, add a review section to the [todo.md](http://todo.md/) file with a summary of the changes you made and any other relevant information.

##Project description
The goal is to create a way for my team to automate the process of identifying scoring issues in the many golf leagues we run on a weekly basis. To do this we need to access several API endpoints and analyze the scoring data so that we can 'Flag' the specific leagues and rounds that may have a scoring issue.

To do this you first need to prompt the user for an API key (user input)

You will then need to access the following API endpoint to retreive all of tthe account's seasons...
https://www.golfgenius.com/api_v2/api_key/seasons

You will then prompt the user to select a season via a list of choices so that the season ID can be used in in a search for all of the events assigned to that seson using this API endpoint...
https://www.golfgenius.com/api_v2/api_key/events?page=page&season=season_id&category=category_id&directory=directory_id&archived=archived

You will then iterate through each of the event's ID's and retrieve all of the round ID's and their associated round dates using this API endpoint...
https://www.golfgenius.com/api_v2/api_key/events/event_id/rounds

You will then allow the golfer to define a date range that will allow you to identify all of the rounds from all of the leagues that fall within that date range.

You will then take the league id and round id from all of the rounds that fall within that date range and use the following API endpoint to iterate through each of the rounds and retreive the golfers scores for the round...
https://www.golfgenius.com/api_v2/api_key/events/event_id/rounds/round_id/tee_sheet?include_all_custom_fields=include_all_custom_fields

You will then analize the scores. We need to know when at least one score (by any player) has been entered on holes 1-9 and at least one score has been entered (by any player) on holes 10-18. Here is an example of the scoring API response, you will see the scores are listed in order 1-18...
[
  {
    "pairing_group": {
      "players": [
        {
          "name": "Wood, Tim",
          "last_name": "Wood",
          "position": 0,
          "tee": {
            "name": "Black",
            "abbreviation": "BLK",
            "hole_data": {
              "par": [
                4,
                4,
                5,
                3,
                4,
                3,
                4,
                5,
                4,
                4,
                3,
                4,
                4,
                5,
                4,
                3,
                5,
                4
              ],
              "yardage": [
                395,
                350,
                492,
                145,
                391,
                196,
                387,
                550,
                343,
                382,
                166,
                340,
                402,
                481,
                446,
                128,
                495,
                347
              ],
              "handicap": [
                7,
                17,
                5,
                13,
                9,
                15,
                3,
                1,
                11,
                8,
                16,
                14,
                4,
                10,
                2,
                18,
                6,
                12
              ]
            },
            "nine_hole_course": false,
            "created_at": "2017-02-22 14:43:52 -0500",
            "updated_at": "2018-02-15 05:56:05 -0500",
            "color": "#000",
            "id": "113916",
            "slope_and_rating": {
              "all18": {
                "rating": 71.3,
                "slope": 131
              },
              "front9": {
                "rating": 36.5,
                "slope": 128
              },
              "back9": {
                "rating": 36.8,
                "slope": 130
              }
            },
            
Your final out put should be the league id's along with the round ID and round Date as a list that we can then address on the on our end.


## Tech Stack
For now this can be a simple python code that I plan on executing in my terminal. 
