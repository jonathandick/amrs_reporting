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
		alert(xhr.status + ": error : " + err);
		result = false;
	    }
	});
    return result;
}

function getDefaulterCohorts(viewCallback) {
    var defaulter_cohorts = local.getItem("defaulter_cohorts");
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
		    success: function(data) { 
			defaulter_cohorts['defaulter_cohorts'] = data;
			local.setItem("defaulter_cohorts",JSON.stringify(defaulter_cohorts));
			viewCallback(defaulter_cohorts)
		    },
		    error : function(xhr,errmsg,err) {
			console.log("ERROR: could not load defaulter cohorts : " + err);
		    }
		});
	    
	}
	else { 	    
	    defaulter_cohorts = JSON.parse(defaulter_cohorts);	    
	    viewCallback(defaulter_cohorts);
	}
    }
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



/* Note that as users are relying on a locally stored list of the defaulter cohorts, it is possible
   that a defaulter cohort they are requesting is now retired. Calling ajax_get_defaulter_cohort
   returns an object containing : "defaulter_cohort", "defaulter_cohorts" and "messages". 
   If there is a new set of defaulter_cohorts, then this will be written to local storage.
*/
function getCohort(id,viewCallback) {
    var key = "defaulter_cohort_id_" + id;    
    var cohort = session.getItem(key); 
    if(cohort === null) {
	console.log("getCohort() : Cohort not in session. Querying server...");
	var data = {defaulter_cohort_id:id};
        //var response = ajaxPOSTSync('/outreach/ajax_get_defaulter_cohort',d);
	var url = '/outreach/ajax_get_defaulter_cohort';
	var response =  $.ajax({
		beforeSend: function() { $.mobile.loading("show"); }, //Show spinner
		complete: function() { $.mobile.loading("hide"); },
		type: "POST",
		url: url,
		data: data,
		dataType: "json",
		success: function(result) { 
		    var cohort = getCohortCallback(result);
		    updateCohort(cohort.id,viewCallback)
		},		    
		error : function(xhr,errmsg,err) {
		    alert(xhr.status + ": error : " + errmsg);
		}
	    });

    } else { 
	console.log("getCohort() : cohort in session and not retired");
	cohort = JSON.parse(cohort);	
	viewCallback(cohort);
    }
}

function getCohortCallback(response) {
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
    return cohort;
}


function setCohort(cohort) {
    var key = "defaulter_cohort_id_" + cohort["id"];
    session.setItem(key,JSON.stringify(cohort));
}




function getNewCohort(id,viewCallback) {
    console.log("getNewCohort() : getting new cohort. old cohort id= " + id);
    var key = "defaulter_cohort_id_" + id;
    console.log("removing key: " + key);
    session.removeItem(key);

    var data = {defaulter_cohort_id:id};
    var url = '/outreach/ajax_get_new_defaulter_cohort';
    var response =  $.ajax({
            beforeSend: function() { $.mobile.loading("show"); }, //Show spinner
            complete: function() { $.mobile.loading("hide"); },
            type: "POST",
            url: url,
            data: data,
            dataType: "json",
            success: function(result) { 
		var cohort = getNewCohortCallback(result);
		viewCallback(cohort);
	    },
            error : function(xhr,errmsg,err) {
                console.log(xhr.status + ": error : " + errmsg);
            }
        }); 
}

function getNewCohortCallback(response) {
    var defaulter_cohorts = {date_created:new Date()};
    defaulter_cohorts["defaulter_cohorts"] = response["defaulter_cohorts"];
    local.setItem("defaulter_cohorts",JSON.stringify(defaulter_cohorts));
    saveCohort(response["defaulter_cohort"]);
    return response["defaulter_cohort"];
}



function isRetired(id) {
    var d = {defaulter_cohort_id:id};
    var response = ajaxPOSTSync('/outreach/ajax_is_defaulter_cohort_retired',d);
    return response;	
}


function updateCohort(id,viewCallback) {
    console.log("updateCohort() : updating cohort...");
    var cohort,numUpdated=0;
    var key = "defaulter_cohort_id_" + id;
    if(navigator.onLine) {
	if(isRetired(id)) {	    
	    console.log("updateCohort() : " + id + " is retired. getting most recent cohort...");
	    session.removeItem(key);
	    cohort = getCohort(id);
	    id = cohort.id
	}
	else {
	    cohort = JSON.parse(session.getItem(key));	    
	}
	var data = {defaulter_cohort_id:id};
	var url = '/outreach/ajax_update_defaulter_cohort';
	var response =  $.ajax({
		beforeSend: function() { $.mobile.loading("show"); }, //Show spinner
		complete: function() { $.mobile.loading("hide"); },
		type: "POST",
		url: url,
		data: data,
		dataType: "json",
		success: function(result) {
		    uc = updateCohortCallback(cohort,result);		    
		    viewCallback(uc[0],uc[1]);
		},
		error : function(xhr,errmsg,err) {
		    console.log(xhr.status + ": error : " + errmsg);
		}
	    });
    }
}


function updateCohortCallback(cohort,updatedPatients) {    
    var key = "defaulter_cohort_id_" + cohort.id;
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
    return [cohort,numUpdated];
}

function getPatient(patient_uuid,cohort_id,viewCallback){
    console.log("getPatient(): patient_uuid: " + patient_uuid + " cohort_id: " + cohort_id);
    var patient;
    if(cohort_id === undefined || cohort_id === "") {
	var patient = session.getItem(patient_uuid);
	if (patient === null) {
	    var data = {patient_uuid:patient_uuid};
	    var response =  $.ajax({
		    beforeSend: function() { $.mobile.loading("show"); }, //Show spinner
		    complete: function() { $.mobile.loading("hide"); },
		    type: "GET",
		    url: "/outreach/ajax_get_patient",
		    data: data,
		    dataType: "json",
		    success: function(patient) { 
			viewCallback(patient);
			session.setItem(patient_uuid,JSON.stringify(patient));			
		    },
		    error : function(xhr,errmsg,err) {
			alert(xhr.status + ": " + errmsg);
		    }
		});	    
	} else { 
	    patient = JSON.parse(patient); 
	    if(viewCallback) {
		viewCallback(patient);
	    }
	    else { return patient };
	}
    }
    else {
	console.log("getPatient() : getting patient from session.cohort");
	var cohort = JSON.parse(session.getItem("defaulter_cohort_id_" + cohort_id));	
	patient = cohort["patients"][patient_uuid];
	session.setItem(patient_uuid,JSON.stringify(patient));
	if(viewCallback) {
	    viewCallback(patient,cohort_id);
	}
	else { return patient; }
    }
}

function getEncounterData(patient_uuid,viewCallback){
    var patient = session.getItem(patient_uuid);    
    if(patient) {
	patient = JSON.parse(patient);
    }

    if(patient && patient.encounterData) {
	console.log("getEncounterData() : encounterData in session");
	viewCallback(patient.encounterData);
    }
    else {
	var data = {patient_uuid:patient_uuid};
	console.log("uuid:" + patient_uuid);
	var response = $.ajax({
		beforeSend: function() { $.mobile.loading("show"); }, //Show spinner
		complete: function() { $.mobile.loading("hide"); },
		type: "GET",
		url: "/outreach/ajax_get_encounter_data",
		data: data,
		dataType: "json",
		success: function(encounterData) { 
		    var patient = JSON.parse(session.getItem(patient_uuid));
		    patient.encounterData = encounterData;
		    session.setItem(patient_uuid,JSON.stringify(patient));
		    console.log("getEncounterData() : encounterData size = " + unescape(encodeURIComponent(JSON.stringify(encounterData))).length);
		    viewCallback(encounterData);
		},
		error : function(xhr,errmsg,err) {
		    console.log("ERROR: could not load encounter data : " + err);
		}
	    });	

    }
}


function getEncounterFull(uuid,viewCallback) {
    var data = {encounter_uuid:uuid};
    var response = $.ajax({
	    beforeSend: function() { $.mobile.loading("show"); }, //Show spinner
	    complete: function() { $.mobile.loading("hide"); },
	    type: "GET",
	    url: "/outreach/ajax_get_encounter_full",
	    data: data,
	    dataType: "json",
	    success: function(encounter) {
		viewCallback(encounter);
	    },
	    error : function(xhr,errmsg,err) {
		console.log("ERROR: could not load encounter data : " + err);
	    }
	});    
}


function getOutreachProviders(viewCallback) {
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
		    success: function(data) { 
			console.log(data);
			providers['providers'] = data; 
			local.setItem("outreach_providers",JSON.stringify(providers));
			if(viewCallback) { viewCallback(providers); }
		    },
		    error : function(xhr,errmsg,err) {
			console.log("ERROR: Could not load providers : " + err);
		    }
		});	
	    
	}    
	else { 
	    providers = JSON.parse(providers); 
	    if(viewCallback) { viewCallback(providers); }
	    else { return providers; }		    
	}
    }
    return providers;   
}


function getLocations(viewCallback) {
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
		    success: function(data) { 
			locations['locations'] = data; 
			local.setItem("outreach_locations",JSON.stringify(locations));
			if(viewCallback) {viewCallback(locations)};
		    },
		    error : function(xhr,errmsg,err) {
			console.log("ERROR: could not load locations : " + err);
		    }
		});	

	}    
	else { 
	    locations = JSON.parse(locations); 
	    if(viewCallback) { viewCallback(locations); }
	    else { return locations; }
	}
    }
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



function patientSearch(search_string,viewCallback) {    
    var data = {search_string:search_string};
    console.log("patientSearch : " + search_string);
    var response = $.ajax({
	    type: "GET",
	    url: "/outreach/ajax_patient_search",
	    data: data,
	    dataType: "json",
	    success: viewCallback,
	    error : function(xhr,errmsg,err) {
		console.log(xhr.status + ": " + errmsg);
	    }
	});
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


