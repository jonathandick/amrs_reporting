$(document).ready(function() {
	var csrftoken = getCookie('csrftoken');
	$.ajaxSetup({
		headers: { "X-CSRFToken": csrftoken }
	    });
	
	$("#test_btn").click(function() {
		ajaxPOST('',onSuccessTest);
	    });
    });



function ajaxPOST(url,data,onSuccessFunction){     
    var response =  $.ajax({
	    type: "POST",
	    url: url,
	    data: data,
	    dataType: "json",
	    success: onSuccessFunction,
	    error : function(xhr,errmsg,err) {
		alert(xhr.status + ": " + errmsg);
	    }
	});
    return response;
}


function ajaxPOSTSync(url,data){     
    var result;
    var response =  $.ajax({
	    type: "POST",
	    url: url,
	    data: data,
	    dataType: "json",
	    success: function(data) { result = data; },
            async:false,
	    error : function(xhr,errmsg,err) {
		alert(xhr.status + ": " + errmsg);
	    }
	});
    return result;
}



function getCohort(id) {
    var key = "defaulter_cohort_id_" + id;

    var cohort = localStorage.getItem(key);
    if(cohort === null) {
	var d = {defaulter_cohort_id:id};
        cohort = ajaxPOSTSync('/ltfu/ajax_get_defaulter_cohort',d);       
 
	d = {name:cohort["name"], date_created:cohort["date_created"],location_uuid:cohort["location_uuid"],id:cohort["id"]};
	var patients = {};
	for(var i=0; i< cohort["patients"].length; i++) {
	    var row = cohort["patients"][i];
	    var uuid = row["patient_uuid"];
	    patients[uuid] = row;
	}
	d["patients"] = patients;	
	localStorage.setItem(key,JSON.stringify(d));
	
    } else { cohort = JSON.parse(cohort) };    
    return cohort;
}

function setCohort(cohort) {
    var key = "defaulter_cohort_id_" + cohort["id"];
    localStorage.setItem(key,JSON.stringify(cohort));
}


function getPatient(patient_uuid,cohort_id){
    var patient;
    if(cohort_id === undefined || cohort_id === "") {
	console.log("getPatient: AJAX request for patient");
	var data = {patient_uuid:patient_uuid};
	var response =  $.ajax({
		type: "GET",
		url: "/outreach_webapp/ajax_get_patient",
		data: data,
		dataType: "json",
		success: function(data) { patient = data; },
		async:false,
		error : function(xhr,errmsg,err) {
		    alert(xhr.status + ": " + errmsg);
		}
	    });	
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
    console.log("Saving encounter to localStorage");
    var u_forms = localStorage.getItem("unsubmitted_forms");
    if(u_forms === null) {
	u_forms = {};
    }
    else {
	u_forms = JSON.parse(u_forms);
    }    
    var s = JSON.stringify(encounter_data);             
    var hash = getHashCode(s);
    u_forms[hash] = encounter_data;
    localStorage.setItem("unsubmitted_forms",JSON.stringify(u_forms));
}


function submitEncounter(data) {
    if(navigator.onLine){
	console.log('Online : Submitting form to server');                    
	var response =  $.ajax({
		type: "POST",
		url: "/ltfu/ajax_submit_encounter",
		data: data,
		dataType: "json",
		error : function() { console.log("AJAX error: saving form to localStorage"); saveEncounter(data);}
	    });    
    } else {
	console.log("Offline : saving form to localStorage");
	saveEncounter(data);
    }
}


function submitSavedEncounter(encounter_data) {
    if(navigator.onLine){
	console.log('Online : Submitting form to server');                    
	var response = $.ajax({
		type: "POST",		
		url: "/ltfu/ajax_submit_encounter",
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
    var u_forms = JSON.parse(localStorage.getItem("unsubmitted_forms"));
    delete u_forms[key];
    var s = $("#submit_saved_forms_link").text("Submit Saved Forms (" + Object.keys(u_forms).length + ")");
    localStorage.setItem("unsubmitted_forms",JSON.stringify(u_forms));
}


function getSavedEncounters(response) {
    var encounters = localStorage.getItem("unsubmitted_forms");    
    if(encounters !== null) {
	encounters = JSON.parse(encounters);
    }
    return encounters;
}



function patientSearch(search_string) {
    var data = {search_string:search_string};
    var result;
    var response =  $.ajax({
	    type: "GET",
	    url: "/outreach_webapp/patient_search",
	    data: data,
	    dataType: "json",
	    success: function(data) { result = data; },
            async:false,
	    error : function(xhr,errmsg,err) {
		alert(xhr.status + ": " + errmsg);
	    }
	});
    return result;
}
