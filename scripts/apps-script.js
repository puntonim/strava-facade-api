/** 
 * This is a copy of the Google App Script used by the Google Sheet
 *  named "Gym sessions log". This script invokes the strava-importer-api"s
 *  Lambda function in order to update Strava.
 *
 * The source of this file is at: https://github.com/puntonim/strava-importer-api/blob/main/scripts/apps-script.js
 */

const API_SECRET = "XXX";  // TODO replace with the real one.

function onOpen() {
  /**
   * Special function run automatically when the Sheet is open.
   */

  // Navigate to the last row right when opening the sheet.
  navigateToLastRow();

  // Add a custom menu to navigate to the last row.
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('Custom Menu')
      .addItem('Go to last row', 'navigateToLastRow')
      .addToUi();
}


function addOneSet() {
    /**
     * Function invoked when clicking on the "+1 set" button.
     * Add one to the selected set counter in Sheet.
     * Used by the +1 drwing button.
     */
    const sheet = SpreadsheetApp.getActiveSheet();

    // Get the position of the +1 button.
    const plusOneButton = sheet.getDrawings()[0];
    const buttonRow = plusOneButton.getContainerInfo().getAnchorRow();
    const buttonCol = plusOneButton.getContainerInfo().getAnchorColumn();

    // Ensure the currently selected cell is on the same row and in a
    //  "reasonable" col.
    const selectedCell = sheet.getSelection().getCurrentCell();
    if (selectedCell.getRow() != buttonRow) {
      _showAlert("Select a cell in the same row as the +1 button");
      return;
    }
    if (selectedCell.getColumn() >= buttonCol) {
      _showAlert("Select a cell at the left of the +1 button");
      return;
    }

    // Finally increment the value.
    let currentValue = selectedCell.getValue();
    if (!currentValue) currentValue = 0;
    selectedCell.setValue(currentValue + 1);
}


class BaseError extends Error {
  constructor(message) {
    super(message);
    this.name = this.constructor.name;
  }
}

class ActivityAlreadyHasDescription extends BaseError { }
class ResponseError extends BaseError { }


function updateStravaDescription() {
  /**
   * Function invoked when clicking on the "Update Strava" button.
   * Get the selected session log and post to my strava-importer-api Lambda
   *  in order make it update the existing Strava activity"s description.
   */
  const selection = SpreadsheetApp.getActiveSpreadsheet().getSelection();
  const activeRange = selection.getActiveRange();

  // Ensure the selected range "looks" valid.
  if (activeRange.getHeight() != 4) {
    _showAlert("The selected range does not seem a valid session log: height != 4");
    return;
  }
  if (activeRange.getWidth() < 1 || activeRange.getWidth() > 20 ) {
    _showAlert("The selected range does not seem a valid session log: 1 > width > 20");
    return;
  }

  // Parse data.
  const date = activeRange.getCell(1, 1).getValue();
  if (!(date instanceof Date)) {
    _showAlert("Not a valid date: " + date);
    return;
  }
  const title = activeRange.getCell(1, 2).getValue();
  const name = "Weight training: " + title[0].toLowerCase() + title.slice(1);
  let exercises = [];
  for (let col = 1; col <= activeRange.getWidth(); col++) {
    const name = activeRange.getCell(2, col).getValue();
    const targetReps = activeRange.getCell(3, col).getValue();
    const sets = activeRange.getCell(4, col).getValue();
    if (!Number.isInteger(sets) || sets < 1 || sets > 90) {
      _showAlert("Not a valid sets counter: " + sets);
      return;
    }
    exercises.push({name: name, reps: targetReps, sets: sets});
  }

  // Send an alert message for "logging" purpose.
  const day_start_ts = Math.round(date / 1000);
  const day_end_ts = day_start_ts + 24 * 60 * 60 - 1;
  const header = "Timestamps: " + day_start_ts + " - " + day_end_ts;
  let description = "";
  for (let exercise of exercises) {
    description += exercise.name + ": " + exercise.reps + " reps x " + exercise.sets + " sets\n"
  }
  _showAlert(header + "\n\n" + name + "\n\n" + description);

  let hasDescriptionAlready = false;

  // Post to my strava-importer-api Lambda.
  try {
    _postToStravaImporterApi(day_start_ts, day_end_ts, description, name);
    return;
  } catch (err) {
    if (err instanceof ActivityAlreadyHasDescription) {
      hasDescriptionAlready = true;
    } else {
      throw err;
    }
  }

  if (!(hasDescriptionAlready)) return;

  const response = _showYesNoAlert("Found an activity with a description already. Overwrite?");
  if (response) {
    const doStopIfDescriptionNotNull = false;
    _postToStravaImporterApi(day_start_ts, day_end_ts, description, name, doStopIfDescriptionNotNull);
  }
}


function _postToStravaImporterApi(afterTs, beforeTs, description, name, doStopIfDescriptionNotNull=true) {
  /**
   * Post to my strava-importer-api Lambda
   *  in order make it update the existing Strava activity"s description.
   */
  Logger.log("START request to Lambda");

  // doStopIfDescriptionNotNull must be a string and not a bool.
  if (doStopIfDescriptionNotNull) doStopIfDescriptionNotNull = "true";
  else doStopIfDescriptionNotNull = "false";

  // Make a POST request with a JSON payload.
  const data = {
    "afterTs": afterTs,
    "beforeTs": beforeTs,
    "description": description,
    "activityType": "WeightTraining",
    "name": name,
    "doStopIfDescriptionNotNull": doStopIfDescriptionNotNull,
  };
  const options = {
    "method": "post",
    "contentType": "application/json",
    "payload": JSON.stringify(data),
    "headers": {
      "authorization": API_SECRET,
    },
    "muteHttpExceptions": true,
  };
  const response = UrlFetchApp.fetch("https://s8afs561v2.execute-api.eu-south-1.amazonaws.com/update-activity-description", options);
  const responseBody = response.getContentText();
  const responseCode = response.getResponseCode();
  Logger.log(responseBody);

  if ((responseCode === 400) && (responseBody.includes("The activity found already has a description"))) {
    throw new ActivityAlreadyHasDescription();
  } else if (responseCode > 299) {
    const msg = "Status code: " + responseCode + "\nBody: " + responseBody;
    _showAlert(`** Error response from Lambda strava-importer-api-*! **\n\n${msg}`);
    throw new ResponseError(msg);
  } else {
    const activityId = JSON.parse(responseBody).id;
    _openUrl("https://www.strava.com/activities/" + activityId, "Opening Strava...");
  }

  Logger.log("END request to Lambda");
}


function _showAlert(text) {
  /**
   * Send an alert message in Sheet.
   */
  SpreadsheetApp.getUi().alert(text);
}


function _showYesNoAlert(text) {
  /**
   * Ask a YES/NO question with an alert message in Sheet and get the response.
   */
  let result = SpreadsheetApp.getUi().alert(text, SpreadsheetApp.getUi().ButtonSet.YES_NO);
  SpreadsheetApp.getActive().toast(`Answer: ${result}`);
  if(result === SpreadsheetApp.getUi().Button.YES) return true;
  return false;
}


function _openUrl(url, message){
  /**
   * Open a URL in a new tab.
   * https://gist.github.com/smhmic/e7f9a8188f59bb1d9f992395c866a047
   */
  const html = HtmlService.createHtmlOutput('<!DOCTYPE html><html><script>'
  +'window.close = function(){window.setTimeout(function(){google.script.host.close()},9)};'
  +'var a = document.createElement("a"); a.href="'+url+'"; a.target="_blank";'
  +'if(document.createEvent){'
  +'  var event=document.createEvent("MouseEvents");'
  +'  if(navigator.userAgent.toLowerCase().indexOf("firefox")>-1){window.document.body.append(a)}'
  +'  event.initEvent("click",true,true); a.dispatchEvent(event);'
  +'}else{ a.click() }'
  +'close();'
  +'</script>'
  // Offer URL as clickable link in case above code fails.
  +'<body style="word-break:break-word;font-family:sans-serif;">Failed to open automatically.  Click below:<br/><a href="'+url+'" target="_blank" onclick="window.close()">Click here to proceed</a>.</body>'
  +'<script>google.script.host.setHeight(55);google.script.host.setWidth(410)</script>'
  +'</html>')
  .setWidth(90).setHeight(1);

  if (!message) {
    message = "Opening " + url + "...";
  }
  SpreadsheetApp.getUi().showModalDialog(html, message);
}


function navigateToLastRow(){
  /**
   * Navigate to the last filled row in the Sheet.
   */
  let ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getActiveSheet();
  sheet.setActiveRange(sheet.getRange(1, 1));
  sheet.setActiveRange(sheet.getRange(sheet.getLastRow(),1));
}
