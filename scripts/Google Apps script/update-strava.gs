class InvalidSelection extends BaseError { }
class NotADate extends BaseError { }
class ActivityAlreadyHasDescription extends BaseError { }
class ActivityNotFound extends BaseError { }
class ResponseError extends BaseError { }


class UpdateStravaButton {
  constructor() {
    this.isCalisthenicsCourse = null;
  }

  click() {
    /**
     * Invoked when clicking on the "Update Strava" button.
     * Get the selected gym session log and post to my strava-facade-api Lambda
     *  in order to update an existing Strava activity's description
     *  or to create a new Strava activity.
     */
    const selection = SpreadsheetApp.getActiveSpreadsheet().getSelection();
    this.activeRange = selection.getActiveRange();

    // Ensure the selected range "seems" valid.
    try {
      this._ensureSelectionIsValid()
    } catch (err) {
      return;
    }

    // Parse data.
    const [dayStartTs, dayEndTs] = this._parseDate();
    const name = this._parseTitle();
    const note = this._parseNote();
    // Detect if it is a regular session log or a calisthenics session at YouReborn.
    this.isCalisthenicsCourse = this._isCalisthenicsCourse(note);
    const exercises = this._parseExercises();

    if (this.isCalisthenicsCourse) { // It's a calisthenics course session at YouReborn.
      const [startTime, duration] = this._askStartTimeAndDuration();
      // TODO NOW INVOKE THE NEW LAMBDA (YET TO BE CREATED) IN ORDER TO CREATE THE NEW ACTIVITY
      showAlert("CALIIIIII - TO BE IMPLEMENTED " + startTime + " " + duration)
    } else { // It's a regular gym session.
      // Send an alert message for "logging" purpose.
      const description = this._sendAlertMessage(dayStartTs, dayEndTs, name, exercises, note);
      // And update the description of the existing Strava activity.
      this._updateStravaActivityDescription(dayStartTs, dayEndTs, description, name)
    }
  }

  _ensureSelectionIsValid() {
    /**
     * Ensure the selected range "seems" valid.
     */
    if (this.activeRange.getHeight() == 4) {
      // A regular gym session log.
      if (this.activeRange.getWidth() < 1 || this.activeRange.getWidth() > 20 ) {
        showAlert("The selected range does not seem a valid session log: 1 > width > 20");
        throw new InvalidSelection();
      }
    } else if (this.activeRange.getHeight() == 1) {
      // A special gym session log like a calisthenics session at Reborn.
      if (this.activeRange.getWidth() != 4 ) {
        showAlert("The selected range does not seem a valid session log: width != 4");
        throw new InvalidSelection();
      }
    } else {
      showAlert("The selected range does not seem a valid session log: height != 4");
      throw new InvalidSelection();
    }
  }

  _parseDate() {
    // Parse data: date.
    const date = this.activeRange.getCell(1, 1).getValue();
    if (!(date instanceof Date)) {
      showAlert("Not a valid date: " + date);
      throw new NotADate();
    }
    const dayStartTs = Math.round(date / 1000);
    const dayEndTs = dayStartTs + 24 * 60 * 60 - 1;
    return [dayStartTs, dayEndTs];
  }

  _parseTitle() {
    // Parse data: title.
    const title = this.activeRange.getCell(1, 2).getValue();
    const name = "Weight training: " + title[0].toLowerCase() + title.slice(1);
    return name;
  }

  _parseNote() {
    // Parse data: optional note.
    const note = this.activeRange.getCell(1, 4).getValue() || null;
    return note;
  }

  _parseExercises() {
    if (this.isCalisthenicsCourse === null) this._isCalisthenicsCourse();

    // Parse data: exercises.
    let exercises = [];
    if (!(this.isCalisthenicsCourse)) {
      for (let col = 1; col <= this.activeRange.getWidth(); col++) {
        const name = this.activeRange.getCell(2, col).getValue();
        const targetReps = this.activeRange.getCell(3, col).getValue();
        const sets = this.activeRange.getCell(4, col).getValue();
        if (!Number.isInteger(sets) || sets < 1 || sets > 90) {
          showAlert("Not a valid sets counter: " + sets);
          return;
        }
        exercises.push({name: name, reps: targetReps, sets: sets});
      }
    }
    return exercises;
  }

  _isCalisthenicsCourse(note=undefined) {
    /**
     * Detect if the session log is a special calisthenics course.
     * It happens if the note is like: "Corso YouReborn: handstand".
     */
    if (note === undefined) note = this._parseNote();

    if (note && note.toLowerCase().includes("youreborn")) {
      this.isCalisthenicsCourse = true;
      return true;
    } else {
      this.isCalisthenicsCourse = false;
      return false;
    }
  }

  _sendAlertMessage(dayStartTs, dayEndTs, name, exercises, note) {
    /**
     * // Send an alert message for "logging" purpose.
     */
    const header = "Timestamps: " + dayStartTs + " - " + dayEndTs;
    let description = "";
    for (let exercise of exercises) {
      description += exercise.name + ": " + exercise.reps + " reps x " + exercise.sets + " sets\n"
    }
    if (note) description += "\n\nNote: " + note.substring(0, 1).toLowerCase() + note.substring(1);
    let alert = header + "\n\n" + name + "\n\n" + description;
    showAlert(alert);
    return description;
  }

  _updateStravaActivityDescription(afterTs, beforeTs, description, name) {
    const stravaFacadeApiClient = new StravaFacadeApiClient();
    let response = null;
    try {
      response = stravaFacadeApiClient.updateActivityDescription(afterTs, beforeTs, description, name);
    } catch (err) {
      if (err instanceof ActivityAlreadyHasDescription) {
        const yesOrNo = showYesNoAlert("Found an activity with a description already. Overwrite?");
        if (yesOrNo) { // "yes" answer.
          response = stravaFacadeApiClient.updateActivityDescription(afterTs, beforeTs, description, name, false);
        } else return;
      } else {
        throw err;
      }
    }

    // Open a new browser tab with the Strava activity.
    const activityId = response.id;
    openUrlInNewBrowserTab("https://www.strava.com/activities/" + activityId, "Opening Strava...");
  }

  _askStartTimeAndDuration() {
    let response = null;
    try {
      response = showPrompt("Start time? Duration?", "Eg. 20:00 1:00");
    } catch (err) {
      throw err;
    }
    // TODO IMPORVE THE PARSING TO MAKE SURE WE GOT INPUT IN THE RIGHT FORMAT!!!! **************************************
    response = response.split(" ");
    const startTime = response[0];
    const duration = response[1];
    return [startTime, duration];
  }
}


class StravaFacadeApiClient {
  updateActivityDescription(afterTs, beforeTs, description, name, doStopIfDescriptionNotNull=true) {
    /**
     * Post to my strava-facade-api Lambda
     *  in order to update an existing Strava activity's description.
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
        "authorization": STRAVA_FACADE_API_SECRET,
      },
      "muteHttpExceptions": true,
    };
    const response = UrlFetchApp.fetch(STRAVA_FACADE_API_BASE_URL + "/update-activity-description", options);
    const responseBody = response.getContentText();
    const responseCode = response.getResponseCode();
    Logger.log(responseBody);

    if ((responseCode === 400) && (responseBody.includes("The activity found already has a description"))) {
      throw new ActivityAlreadyHasDescription();
    } else if (responseCode === 404) {
      throw new ActivityNotFound();
    } else if (responseCode > 299) {
      const msg = "Status code: " + responseCode + "\nBody: " + responseBody;
      showAlert(`** Error response from Lambda strava-facade-api-*! **\n\n${msg}`);
      throw new ResponseError(msg);
    }
    Logger.log("END request to Lambda");
    return JSON.parse(responseBody);
  }
}
