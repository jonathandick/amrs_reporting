//Function to obtain the option for how to write to local file system. By default configured to localStorage

function getLocalStorage() {
    return localStorage;
}

function getSessionStorage() {
    return sessionStorage;
}

var local = getLocalStorage();
var session = getSessionStorage();

$(document).ready(function() {
	var csrftoken = getCookie('csrftoken');
	$.ajaxSetup({
		headers: { "X-CSRFToken": csrftoken }
	    });
	
	$("#test_btn").click(function() {
		ajaxPOST('',onSuccessTest);
	    });
    });


//Needed for Django
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function ajaxPOST(url,data,onSuccessFunction){     
    var response =  $.ajax({
	    type: "POST",
	    url: url,
	    data: data,
	    dataType: "json",
	    success: onSuccessFunction,
	    error : function(xhr,errmsg,err) {
		alert(xhr.status + ": error : " + errmsg);
	    }
	});
    return response;
}


function ajaxPOSTSync(url,data){     
    var result;
    var response =  $.ajax({
	    beforeSend: function() { $.mobile.loading("show"); }, //Show spinner
            complete: function() { $.mobile.loading("hide"); },
	    type: "POST",
	    url: url,
	    data: data,
	    dataType: "json",
	    success: function(data) { result = data; },
            async:false,
	    error : function(xhr,errmsg,err) {
		console.log(xhr.status + ": error : " + errmsg);
		result = false;
	    }
	});
    return result;
}



//Cohort is expected to be from server. In this case patients are an array. 
//We need to convert to object indexed by patient uuid for local storage.
function saveCohort(cohort) {
    var c = {name:cohort["name"], date_created:cohort["date_created"],location_uuid:cohort["location_uuid"],id:cohort["id"]};
    var patients = {};
    for(var i=0; i< cohort["patients"].length; i++) {
	var row = cohort["patients"][i];
	var uuid = row["uuid"];
	patients[uuid] = row;
    }
    c["patients"] = patients;
    var key = "defaulter_cohort_id_" + cohort["id"];    
    session.setItem(key,JSON.stringify(c));
    console.log("saveCohort() : cohort saved to session");
}


function isRetired(id) {
    var d = {defaulter_cohort_id:id};
    var response = ajaxPOSTSync('/outreach/ajax_is_defaulter_cohort_retired',d);
    return response;	
}



/* Note that as users are relying on a locally stored list of the defaulter cohorts, it is possible
   that a defaulter cohort they are requesting is now retired. Calling ajax_get_defaulter_cohort
   returns an object containing : "defaulter_cohort", "defaulter_cohorts" and "messages". 
   If there is a new set of defaulter_cohorts, then this will be written to local storage.
*/
function getCohort(id) {
    var key = "defaulter_cohort_id_" + id;    
    var cohort = session.getItem(key); 
    if(cohort === null) {
	console.log("getCohort() : Cohort not in session. Querying server...");
	var d = {defaulter_cohort_id:id};
        var response = ajaxPOSTSync('/outreach/ajax_get_defaulter_cohort',d);
	var cohort = response["defaulter_cohort"];
	saveCohort(cohort);
	if("messages" in response) {
	    alert(response["messages"]);
	}
	if("defaulter_cohorts" in response) { 
	    var defaulter_cohorts = {date_created:new Date()};
	    defaulter_cohorts["defaulter_cohorts"] = response["defaulter_cohorts"];
	    local.setItem("defaulter_cohorts",JSON.stringify(defaulter_cohorts));
	}
	cohort = updateCohort(cohort.id);
    } else { 
	console.log("getCohort() : cohort in session and not retired");
	cohort = JSON.parse(cohort);	
    }
    
    return cohort;
}



function setCohort(cohort) {
    var key = "defaulter_cohort_id_" + cohort["id"];
    session.setItem(key,JSON.stringify(cohort));
}


function getNewCohort(id) {
    console.log("getNewCohort() : getting new cohort. old cohort id= " + id);
    var key = "defaulter_cohort_id_" + id;
    console.log("removing key: " + key);
    var d = {defaulter_cohort_id:id};
    var response = ajaxPOSTSync('/outreach/ajax_get_new_defaulter_cohort',d);
    
    if(response !== null) {
	var defaulter_cohorts = {date_created:new Date()};
	defaulter_cohorts["defaulter_cohorts"] = response["defaulter_cohorts"];
	local.setItem("defaulter_cohorts",JSON.stringify(defaulter_cohorts));
	session.removeItem(key);
	saveCohort(response["defaulter_cohort"]);
    }
        
    return response["defaulter_cohort"];
}


function updateCohort(id) {
    console.log("updateCohort() : updating cohort...");
    var key = "defaulter_cohort_id_" + id;
    var d = {defaulter_cohort_id:id};
    var updatedPatients = ajaxPOSTSync('/outreach/ajax_update_defaulter_cohort',d);
    console.log("updateCohort() " + updatedPatients.length + " retired patients");

    var cohort = JSON.parse(session.getItem(key));
    var numUpdated = 0;
    if(updatedPatients !== null) {
	for(var i=0; i<updatedPatients.length; i++) {
	    var patient_uuid = updatedPatients[i];
	    if(patient_uuid in cohort.patients) {
		var p = cohort.patients[patient_uuid];
		if(p.retired == 0) {
		    cohort.patients[patient_uuid].retired=1;
		    numUpdated++;
		}
	    }
	}
	session.setItem(key,JSON.stringify(cohort));
    }
    alert(numUpdated + " patients updated.");
    return cohort;
}


function getPatient(patient_uuid,cohort_id){
    console.log("getPatient(): patient_uuid: " + patient_uuid + " cohort_id: " + cohort_id);
    var patient;
    if(cohort_id === undefined || cohort_id === "") {
	var patient = null; //session.getItem(patient_uuid);
	if (patient === null) {
	    var data = {patient_uuid:patient_uuid};
	    var response =  $.ajax({
		    type: "GET",
		    url: "/outreach/ajax_get_patient",
		    data: data,
		    dataType: "json",
		    success: function(data) { patient = data; },
		    async:false,
		    error : function(xhr,errmsg,err) {
			alert(xhr.status + ": " + errmsg);
		    }
		});	
	    //session.setItem(patient_uuid,JSON.stringify(patient));
	} else { patient = JSON.parse(patient); }
    }
    else {
	var cohort = getCohort(cohort_id);
	patient = cohort["patients"][patient_uuid];
    }
    return patient
}


function getHashCode(s) {
    var hash = 0, i, chr, len;
    if (s.length == 0) return hash;
    for (i = 0, len = s.length; i < len; i++) {
	chr   = s.charCodeAt(i);
	hash  = ((hash << 5) - hash) + chr;
	hash |= 0; // Convert to 32bit integer
    }
    return hash;
}


function saveEncounter(encounter_data) {
    console.log("Saving encounter to local");
    var u_forms = local.getItem("unsubmitted_forms");
    if(u_forms === null) {
	u_forms = {};
    }
    else {
	u_forms = JSON.parse(u_forms);
    }    
    var s = JSON.stringify(encounter_data);             
    var hash = getHashCode(s);
    u_forms[hash] = encounter_data;
    local.setItem("unsubmitted_forms",JSON.stringify(u_forms));
}


function submitEncounter(data) {
    if(navigator.onLine){
	console.log('Online : Submitting form to server');                    
	var response =  $.ajax({
		type: "POST",
		url: "/outreach/ajax_submit_encounter",
		data: data,
		dataType: "json",
		success: function() { alert("Form submitted"); },
		error : function() { console.log("AJAX error: saving form to local"); saveEncounter(data);}
	    });    
    } else {
	console.log("Offline : saving form to local");
	saveEncounter(data);
    }
}


function submitSavedEncounter(encounter_data) {
    if(navigator.onLine){
	console.log('Online : Submitting form to server');                    
	var response = $.ajax({
		type: "POST",		
		url: "/outreach/ajax_submit_encounter",
		data: encounter_data,
		dataType: "json",
		success: onSuccessSubmitSavedEncounter,
		error : function(xhr,errmsg,err) {
		    console.log("submitSavedForm : AJAX Error : " + xhr.status + ": " + errmsg);
		}	    
	    }); 
    }
}


function onSuccessSubmitSavedEncounter(response) {
    var key = response["key"];
    console.log("Saved form submitted successfully. Key = " + key);
    var u_forms = JSON.parse(local.getItem("unsubmitted_forms"));
    delete u_forms[key];
    var s = $("#submit_saved_forms_link").text("Submit Saved Forms (" + Object.keys(u_forms).length + ")");
    local.setItem("unsubmitted_forms",JSON.stringify(u_forms));
}


function getSavedEncounters(response) {
    var encounters = local.getItem("unsubmitted_forms");    
    if(encounters !== null) {
	encounters = JSON.parse(encounters);
    }
    return encounters;
}



function patientSearch(search_string,onSuccessFunction) {    
    var data = {search_string:search_string};
    console.log("patientSearch : " + search_string);
    if(onSuccessFunction === undefined || onSuccessFunction === "") {	
	var result;    
	var response =  $.ajax({
		type: "GET",
		url: "/outreach/ajax_patient_search",
		data: data,
		dataType: "json",
		success: function(data) { result = data; },
		async:false,
		error : function(xhr,errmsg,err) {
		    console.log(xhr.status + ": " + errmsg);
		}
	    });	
	return result;
    }
    else {
	console.log("async");
	var response = $.ajax({
                type: "GET",
		url: "/outreach/ajax_patient_search",
		data: data,
		dataType: "json",
		success: onSuccessFunction,
		error : function(xhr,errmsg,err) {
                    console.log(xhr.status + ": " + errmsg);
                }
	    });
    }
}


function updatePhoneNumber(patient_uuid,number) {
    var d = {phone_number:number,patient_uuid:patient_uuid};
    var response = $.ajax({
	    type: "POST",
	    url: "/outreach/ajax_update_phone_number",
	    data: d,
	    dataType: "json",
	    success: function() {
               alert("Phone number updated.");
            },
	    error : function(xhr,errmsg,err) {
		alert("ERROR: Phone number not updated : " + err);
	    }
	});
}


function getOutreachProviders() {
    var providers = local.getItem("outreach_providers");
    var seven_days_ago = new Date();
    seven_days_ago.setDate(seven_days_ago.getDate() - 7);

    if(navigator.onLine) {
	if(providers === null || (new Date(JSON.parse(providers).date_created )) < seven_days_ago) { 
	    console.log("Loading providers...");
	    providers = {date_created:new Date()};    
	    var response = $.ajax({
		    type: "GET",
		    url: "/outreach/ajax_get_outreach_providers",
		    dataType: "json",
		    async: false,
		    success: function(data) { providers['providers'] = data; },
		    error : function(xhr,errmsg,err) {
			console.log("ERROR: Could not load providers : " + err);
		    }
		});	
	    local.setItem("outreach_providers",JSON.stringify(providers));
	}    
	else { providers = JSON.parse(providers); }
    }
    return providers;   
}

function getOutreachLocations() {
    var locations = local.getItem("outreach_locations");
    var seven_days_ago = new Date();
    seven_days_ago.setDate(seven_days_ago.getDate() - 7);

    if(navigator.onLine) {
	if(locations === null || (new Date(JSON.parse(locations).date_created)) < seven_days_ago) { 
	    console.log("Loading locations...");
	    locations = {date_created:new Date()};    
	    var response = $.ajax({
		    type: "GET",
		    url: "/outreach/ajax_get_locations",
		    dataType: "json",
		    async: false,
		    success: function(data) { locations['locations'] = data; },
		    error : function(xhr,errmsg,err) {
			console.log("ERROR: could not load locations : " + err);
		    }
		});	
	    local.setItem("outreach_locations",JSON.stringify(locations));
	}    
	else { locations = JSON.parse(locations); }
    }
    return locations;   
}



function getDefaulterCohorts() {
    var defaulter_cohorts = null; //local.getItem("defaulter_cohorts");
    var seven_days_ago = new Date();
    seven_days_ago.setDate(seven_days_ago.getDate() - 7);
    if(navigator.onLine) {
	if(defaulter_cohorts === null || (new Date(JSON.parse(defaulter_cohorts).date_created)) < seven_days_ago) { 	    
	    console.log("Loading defaulter_cohorts...");
	    defaulter_cohorts = {date_created:new Date()};    
	    var response = $.ajax({
		    type: "GET",
		    url: "/outreach/ajax_get_defaulter_cohorts",
		    dataType: "json",
		    async: false,
		    success: function(data) { defaulter_cohorts['defaulter_cohorts'] = data; },
		    error : function(xhr,errmsg,err) {
			console.log("ERROR: could not load defaulter cohorts : " + err);
		    }
		});
	    local.setItem("defaulter_cohorts",JSON.stringify(defaulter_cohorts));
	}
	else { defaulter_cohorts = JSON.parse(defaulter_cohorts); }
    }
    return defaulter_cohorts;   
}


function getEncounterData(patient_uuid){
    var encounterData = session.getItem(patient_uuid);
    if(encounterData === null) {
	var data = {patient_uuid:patient_uuid};
	console.log("uuid:" + patient_uuid);
	var response = $.ajax({
		type: "GET",
		url: "/outreach/ajax_get_encounter_data",
		data: data,
		dataType: "json",
		async: false,
		success: function(data) { encounterData = data; },
		error : function(xhr,errmsg,err) {
		    console.log("ERROR: could not load encounter data : " + err);
		}
	    });
	session.setItem(patient_uuid,JSON.stringify(encounterData));
	console.log("getEncounterData() : encounterData size = " + unescape(encodeURIComponent(JSON.stringify(encounterData))).length);
    }
    else {
	console.log("getEncounterData() : encounterData in session");
	encounterData = JSON.parse(encounterData);
    }
    return encounterData;
}