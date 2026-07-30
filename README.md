<h1>Email Tracker Agent</h1>
<br>
<h2> Goal </h2>
This agent will read your gmail emails from the last 2 weeks, it'll look for emails related to job applications and determine the status of the application. When it finds emails related to job applications it will check if its being tracked currently and if not will begin tracking it in a google spreadsheet. The goal was to cut down manual labor in making a spreadsheet showing which companies I have applied to and what state the application is in. Applying to jobs took twice as long as I had to apply, manually make a row with the company name, status, and other information. Now it will add them automatically and even keep applications up to date.

<h2>Setup</h2>
<ol>
    <li>
    First we must get the requirements to use the agent.<br>
    <code>pip install -r requirements.txt</code>
    </li>
    <li>
    Then we can simply call the function<br>
    <code>python main.py</code>
    </li>
    <li>
    When prompted you will need to give the agent a prompt to initiate the interaction such as:<br>
    <code>Check my email for any updates.</code>
    </li>
</ol>

<h2>Future Plans</h2>
- [x]Integrate Docker to make setup more straightforward<br>
- [x]Setup email summaries to be sent to a configed email summarizing what was found and what actions were done<br>
- Adding follow-up email recommendations<br>
- Checking sent emails for extra information<br>
- Add integrated tests<br>
- [x]Make CI pipeline