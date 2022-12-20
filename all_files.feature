@pinProject

	@pinProjectButton
Scenario: As a user, I want to pin important projects/tasks to prioritize certain activities.
Given I am on the Projects page
When I see the pin button attached to each project
And I click the pin button for the project I want to pin as important
Then I see the important project now pinned at the top of the page

@createProject:

	@createProjectButton
Senario: Opening the create new project screen

Given I am on the create projects tab
When I click create project
Then the creation window will pop up
Then a name window will appear
Then I fill in that window
And the new project is ready to be made

@createNameTextbox
Senario: Giving a name to a new project

Given I clicked create project
When I open that I should see a name textbox
Then I should be able to give my new project a name
But I cannot leave it blank
Then I click submit
And the new project is filled out with details

@createProjectFinishButton
Senario: Finishing new project creation

Given I am in the create project window
And I have filled out the rest of the window
Then I should be able to click finish
But I can also press cancel to disregard all changes
Then I click submit
And the new project is created
And the new project is added to project list

@createComment:

@createCommentButton
Senario: Creating a new comment

Given I am logged in
And I open an existing project
When I click the comment button
Then I should be able to view other comments
Then a window should pop up
Then I should be able to fill in a textbox with the title
And I should be able to fill in a textbox with the comment
When I click the submit button the comment is created
And the pop up window should disappear
But I should be able to close the pop up window at any time before creating a comment by clicking on an X button

@test_registerUser:

@newUserButton
Senario: Load create new user screen

Given I am on the create new user screen
And I click on create new user
Then the new user page will load
Then account required information window appear
Then I fill out window
And User is ready to be created

	@createCreateUser
Senario:

Given I filled in the required info and am on new user screen
When I click create new user
Then page checks for preexisting user
But if there is no preexisting user
Then new user is added to database
And the new user can now log in
