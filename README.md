# POLLSTER

Pollster is a simple, free, easy-to-use web application that allows users to create polls. Polls are open to the public by default, but can be created and shared privately as well.

## About the Authors

My name is David Bogaerts.

## Getting Started/Installation Notes/System Specifications

This application works on all modern web browsers.

## How to Use the Application

## User Stories

1. user will go to the website's main page. User can either log in or view active polls. User may view active polls, but cannot respond to them without logging in. 

2. Registration: User can click the registration link if he or she does not have an account. User will be prompted to provide certain information for registration, including username (must be unique), email address (must be unique), and a password. Once user's account is created, he or she will be redirected by to the home page. 

3. While logged in: All logged-in users have the ability to create polls and participate in active polls. 

4. Poll participation: A user may browse and review polls in the following ways:
  * Browse button (shows user a list of all polls)

    The viewable list includes all public polls, and all private polls to which the user has access. By default, polls are sorted via date and time posted. Polls may also be re-ordered by how much time is left before the poll expires. The browse button also can display all expired polls so that users can review poll results.

  * Random button (shows user a random active poll)

  * Invitation code (user enters invitation code into form in order to access specific poll-code provided by poll creator.

5. Creating a poll: a logged-in user may opt to create a poll. User defines the question and two-to-four responses. All question and response fields are character count limited.  The user also selects (1) whether the poll is public or private, (2) the date and time the poll expires, and (3) if the poll is private, the usernames of those people who are invited to participate in the poll. Poll results are available indefinitely after a poll expires (unless the poll creator deletes the poll). Additionally, when the user creates a poll, it is automatically assigned an invitation hash code. This code is viewable to anyone that has access to the poll, and can be used to quickly access it from the homepage. 

6. Voting: If a user views a poll that he or she has not voted on, user will see the question and the available responses. User may click on any response to vote on the poll. Once user has voted, or the poll has expired, the response buttons will be replaced with a bar graph depicting the status of voting. Current voting status is not viewable if the poll is active, and the viewing user has not voted on the poll. 

7. Other use-related notes: Only the user that creates a poll may delete or edit it. If the user edits the content of the poll question or possible responses after people have started responding to it, poll responses will be purged, and the poll will be reset. Other users may update poll by voting on it. 

## Upcoming features

TBD
