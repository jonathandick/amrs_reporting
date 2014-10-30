function appsView() {
    $(".app").hide();
    $("#apps_view").css("display","inline");
    var encounters = getSavedEncounters();
    var numEncounters = Object.keys(encounters).length;
    $("#apps_view #num_saved_encounters").text(numEncounters)
}

function initDefaulterCohortListView() {
    var list = $("#defaulter_cohort_list_view #defaulter_cohort").empty();
    list.append("<option/>");
    var dcs = getDefaulterCohorts();
    for(var i=0; i < dcs.defaulter_cohorts.length; i++) {
	dc = dcs.defaulter_cohorts[i];
	list.append("<option value='" + dc.id + "'>" + dc.name + "</option>");
    }
}


function defaulterCohortListView(){
    $(".app").hide();
    var cur_list_id = $("#list_defaulter_cohort_id").val();
    var id = $("#defaulter_cohort").val();
    if((id !== "") && ((id != cur_list_id) || ($("#defaulter_cohort_list li").length == 0)))  {	
	var cohort = getCohort(id);
	initDefaulterCohortListView();
	$("#defaulter_cohort_list_view #defaulter_cohort_name").text(cohort["name"]);
	$("#defaulter_cohort_list_view #date_created").text(cohort["date_created"]);
	defaulterCohortToList(cohort);
    }
    /*
    else {
	updateCohort(cur_list_id);
    }
    */
    $("#defaulter_cohort_list_view").css("display","inline");
}



//key : defaulter_cohort_id_NN
function defaulterCohortToList(cohort) {			    
    $("#defaulter_cohort_list").empty();
    var patients = cohort["patients"];
    var key = "defaulter_cohort_id_" + cohort["id"];
    var total_patients = Object.keys(patients).length; 
    var num_remaining = total_patients;
    var risk_categories = {0:'Being Traced',1:'High',2:'Medium',3:'Low',4:'LTFU',5:'no_rtc_date',6:'Untraceable'};

    for(var uuid in patients) {           
	var row = patients[uuid];
	var s = "<li";
	if(row['retired']) {
	    s += " class='retired'";
	    num_remaining = num_remaining - 1;
	}
	s += "><a onClick=\"patientDashboardView('" + row["uuid"] + "','" + cohort["id"] + "')\">";
	s += row["family_name"] + ", " + row["given_name"] + " " + row["middle_name"] + "<br/>";
	s += row["identifier"] + "<br/>";
	s += "Phone: " + row["phone_number"] + "<br/>";
	s += "Risk Category: " + risk_categories[row.risk_category]
	$("#defaulter_cohort_list").append(s).listview("refresh");    	  
    }
    $("#list_location_uuid").val(cohort["location_uuid"]);
    
    var id = cohort["id"];
    $("#list_defaulter_cohort_id").val(id);
    $("#defaulter_cohort_list_view #num_remaining").text("Patients remaining to be traced: " + num_remaining + " / " + total_patients);        

}



function tbDataToTable(tbData) {
    $("#dash_tb_data > tbody").empty(); //).find("tr:gt(0)").remove();
    var obs_order = ["TB Prophylaxis","TB Prophylaxis Plan","TB Prophylaxis Stop Reason",
		     "TB Tx Start Date","Start Reason","Current TB Meds","TB tx Plan","Stop/Change Reason","New TB Drugs"
		     ];
    
    $("#dash_tb_data_table").remove();    
    s = '<table id="dash_tb_data_table" data-role="table" data-mode="columntoggle" class="ui-responsive ui-body-d table-stripe">';
    s += '<thead class="ui-bar-d" data-position="fixed"><tr>';
    s += '<th>Date</th>';
    for(var i=0; i<obs_order.length; i++) {
	s += '<th data-priority="1">' + obs_order[i] + "</th>";
    }
    s += '</tr></thead>';        
       
    var keys = Object.keys(tbData).sort();
    for(var i=0; i<keys.length; i++) {	
	var row = tbData[keys[i]];
	s += "<tr>";
	s += "<td>" + row["encounter_datetime"].substring(0,10) + "</td>";
	for(var j=0; j<obs_order.length; j++) {
	    s += "<td>";
	    var vals = row.obs[obs_order[j]];
	    if(vals !== undefined) {
		for(var k=0; k<vals.length; k++) {
		    s += " " + vals[k] + "<br/>";
		}
	    }
	    s += "</td>";
	}
	s += "</tr>";
    }
    $("#dash_tb_data_table-popup-popup").remove(); 
    $("#dash_tb_data").html(s).enhanceWithin();
    $("#dash_tb_data").show();
}

function encounterDataToTable(encounterData) {
    $("#dash_encounter_data > tbody").empty(); //).find("tr:gt(0)").remove();

    var obs_order = ["WEIGHT (KG)","CD4, BY FACS","HIV VIRAL LOAD, QUANTITATIVE","LAB RESULTS","TESTS ORDERED",
		     "PROBLEM ADDED",
		     "CURRENT ANTIRETROVIRAL DRUGS USED FOR TREATMENT","ANTIRETROVIRAL PLAN","ANTIRETROVIRALS STARTED",
		     "MEDICATION ORDERS",
		     ];
    
    var keys = Object.keys(encounterData.core).sort();
    console.log("encounterDataToTable() : number of encounters = " + keys.length);

    $("#dash_encounter_data_table").remove();
    s = '<table id="dash_encounter_data_table" data-role="table" data-mode="columntoggle" class="ui-responsive ui-body-d table-stripe">';
    s += '<thead class="ui-bar-d" data-position="fixed"><tr>';
    s += '<th>Date</th>';
    s += '<th data-priority="1">Type</th>';
    s += '<th data-priority="1">Clinic</th>';
    s += '<th data-priority="1">Provider</th>';
    s += '<th data-priority="1">RTC Date</th>';
    s += '<th data-priority="1">Weight</th>';
    s += '<th data-priority="1">CD4</th>';
    s += '<th data-priority="1">VL</th>';
    s += '<th data-priority="1">Lab Data</th>';
    s += '<th data-priority="1">Tests Ordered</th>';
    s += '<th data-priority="1">Problem(s)</th>';
    s += '<th data-priority="1">ARVs</th>';
    s += '<th data-priority="1">ARV Plan</th>';
    s += '<th data-priority="1">New ARVs</th>';
    s += '<th data-priority="1">Med Orders</th>';
    s += '</tr></thead>';
        


    
    var curDate,deadline = new Date(encounterData.core[keys[0]].obs["RETURN VISIT DATE"]);
    deadline.setDate(deadline.getDate() + 30);

    for(var i=0; i<keys.length; i++) {
	var row = encounterData.core[keys[i]];

	s += "<tr";	
	if(row["encounter_type"] !== undefined && row.encounter_type.toLowerCase() != "outreachfieldfu") {
	    curDate = new Date(row["encounter_datetime"]);
	    if(curDate > deadline) {		
		s += " style='background-color:#ffb6c1'";
	    }
	    if(row.obs["RETURN VISIT DATE"] !== undefined) {		
		deadline = new Date(row.obs["RETURN VISIT DATE"]);
		deadline.setDate(deadline.getDate() + 30);
	    }
	}
	s += ">";
	

	s += "<td>" + row["encounter_datetime"].substring(0,10) + "</td>";
	s += "<td>" + row["encounter_type"] + "</td>";
	s += "<td>" + row["location"] + "</td>";
	s += "<td>" + row["provider"] + "</td>";
	s += "<td>";
	if(row.obs["RETURN VISIT DATE"] !== undefined) {
	    s += row.obs["RETURN VISIT DATE"][0].substring(0,10);
	}
	s += "</td>";
	for(var j=0; j<obs_order.length; j++) {
	    s += "<td>";
	    var vals = row.obs[obs_order[j]];
	    if(vals !== undefined) {
		for(var k=0; k<vals.length; k++) {
		    s += " " + vals[k] + "<br/>";
		}
	    }
	    s += "</td>";
	}
	s += "</tr>";
    }
    $("#dash_encounter_data_table-popup-popup").remove(); 
    $("#dash_encounter_data").html(s).enhanceWithin();
    $("#dash_encounter_data").show();    
}


function getEncounterDataView() {
    if(navigator.onLine) {
	var patientUuid = $("#dash_patient_uuid").val();
	var encounterData = getEncounterData(patientUuid);
	encounterDataToTable(encounterData);
	tbDataToTable(encounterData.tb);	
    }
    else {
	alert('You must be online to access encounter data');
    }
}

function getNewDefaulterCohortView() {
    var id = $("#list_defaulter_cohort_id").val();
    if(id === "") {
	alert("You must first load a clinic.");
    }
    else if(confirm('This will retire the current list. Are you sure you want to create a new defaulter list?')) {
	var cohort = getNewCohort(id);
	$("#defaulter_cohort_list_view #defaulter_cohort_name").text(cohort["name"]);
	$("#defaulter_cohort_list_view #date_created").text(cohort["date_created"]);
	defaulterCohortToList(cohort);
	initDefaulterCohortListView();
	$("#list_defaulter_cohort_id").val(cohort.id);
	$("#defaulter_cohort").val(cohort.id);
	$("#defaulter_cohort").selectmenu("refresh");	
	alert("New cohort loaded");
    }    
}


function updateDefaulterCohortView() {
    var id = $("#list_defaulter_cohort_id").val();
    if(id === "") {
	alert("You must first load a clinic.");
    }
    else {
	var cohort = updateCohort(id);
	defaulterCohortToList(cohort);
    }
}



function patientDashboardView(patient_uuid,cohort_id) {
    $(".app").hide();
    $("#dash_encounter_data").empty(); //).find("tr:gt(0)").remove();

    $("#patient_dashboard_view").css("display","inline");    
    var patient = getPatient(patient_uuid,cohort_id);

    $("#dash_patient_name").text(patient["given_name"] + " " + patient["middle_name"] + " " + patient["family_name"]);
    $("#dash_identifier").text(patient["identifier"]);
    $("#dash_birthdate").text(patient["birthdate"].substring(0,10));
    $("#dash_phone_number").val(patient["phone_number"]);
    $("#dash_patient_uuid").val(patient["uuid"]);

    $("#dash_last_encounter_date").text(patient.last_encounter_date);
    $("#dash_last_encounter_type").text(patient["last_encounter_type"]);
    $("#dash_last_rtc_date").text(patient["last_rtc_date"]);

    $("#dash_encounters").find("tr:gt(0)").remove();

    if(cohort_id === undefined || cohort_id === null || cohort_id === "") {
	$("#dash_back_button").attr("onClick","patientSearchView()");
    }
    else {
	$("#dash_back_button").attr("onClick","defaulterCohortListView()");
    }

    var s = "";
    for(var i=0;i<patient.encounters.length;i++) {
	var e = patient.encounters[i];
	s += "<tr><td>" + e.encounterDatetime.substring(0,10) + "</td><td>" + e.location.name + "</td><td>" + e.encounterType.name + "</td></tr>";	
    }
    $("#dash_encounters tr:last").after(s);
}


function initOutreachFormView() {
    var outreach_locations = $("#outreach_form_view #location_uuid");
    var transfer_locations = $("#outreach_form_view #transfer_location");
    if(outreach_locations.size() == 1) {
	var locations = getOutreachLocations();	
	for(var i=0; i <locations.locations.length; i++) {
	    l = locations.locations[i];
	    outreach_locations.append("<option value='" + l.uuid + "'>" + l.name + "</option>");
	    transfer_locations.append("<option value='" + l.location_id + "'>" + l.name + "</option>");
	}
    }
    
    var outreach_providers = $("#outreach_form_view #provider_uuid");
    if(outreach_providers.size() == 1) {
	var providers = getOutreachProviders();
	for(var i=0; i<providers.providers.length;i++) {
	    var p = providers.providers[i];
	    outreach_providers.append("<option value='" + p.uuid + "'>" + p.given_name + " " + p.family_name + "</option>");
	}
    }

    $("#patient_status").rules("add",{required:true});
    $("#date_found").rules("add",{needs_date_found:true});
    $("#location_of_contact").rules("add",{needs_location_of_contact:true});
    $("#return_visit_date").rules("add",{needs_rtc_date:true});
    $("#likelihood_of_return").rules("add",{needs_likelihood_of_return:true});
    $("#transfer_location").rules("add",{needs_transfer_location:true});
    $("#phone_number").rules("add",{needs_phone_number:true});
    $("#date_of_death").rules("add",{needs_death_info:true});
    $("#date_of_death").rules("add",{check_death_date:true});
    $("#cause_for_death").rules("add",{needs_death_info:true});
    $("#provider_uuid").rules("add",{required:true});
    $("#encounter_datetime").rules("add",{required:true});
    
}


function initDefaulterCohortListView() {
    var list = $("#defaulter_cohort_list_view #defaulter_cohort").empty();
    list.append("<option/>");
    var dcs = getDefaulterCohorts();
    for(var i=0; i < dcs.defaulter_cohorts.length; i++) {
	dc = dcs.defaulter_cohorts[i];
	list.append("<option value='" + dc.id + "'>" + dc.name + "</option>");
    }
}



function outreachFormView(){
    $(".app").hide();
    $("#outreach_form_view").css("display","inline");	
    
    var cohort_id = $("#list_defaulter_cohort_id").val();    
    var patient_uuid = $("#dash_patient_uuid").val();
    var patient = getPatient(patient_uuid,cohort_id);
    

    $("#return_to_dashboard").attr("onClick","patientDashboardView('" + patient["uuid"] + "')");

    $("#outreach_form_view input[auto-populate='True']").each(function(index) {
	    $(this).attr("value",(patient[$(this).attr("id")])); 
	});
    
    
    $("#outreach_form #location_uuid").val($("#list_location_uuid").val()).selectmenu("refresh");
    $("#outreach_form #defaulter_cohort_id").val($("#list_defaulter_cohort_id").val());
    
    var today = new Date();
    var yyyy = today.getFullYear().toString();
    var mm = (today.getMonth()+1).toString(); // getMonth() is zero-based
    var dd  = today.getDate().toString();
    var s = yyyy + "-" + (mm[1]?mm:"0"+mm[0]) + "-" + (dd[1]?dd:"0"+dd[0]); // padding
    $("#encounter_datetime").val(s);
}    



function submitOutreachFormView() {
    errors = validateDates();
   

    if($("#outreach_form").valid() && errors === "") {
        var d = getFormData($("#outreach_form"));
	submitEncounter(d);
        $("#outreach_form").trigger("reset");
        var id = $("#outreach_form #defaulter_cohort_id").val();
        var patient_uuid = $("#outreach_form #uuid").val();
	if(id !== null && id !== "") {
	    retirePatient(id,patient_uuid);
	    $("#defaulter_cohort_list").empty();
	    defaulterCohortListView();
	}
	else { 
	    $("#patient_search_view #search_string").val("");
	    appsView(); 
	}
    } else {
	alert("This form has errors. Please correct them before submitting");
    }
}


function retirePatient(cohort_id,patient_uuid) {
    var cohort = getCohort(cohort_id);
    cohort.patients[patient_uuid].retired=1;
    setCohort(cohort);
}


function getFormData($form){
    var unindexed_array = $form.serializeArray();
    var indexed_array = {};
    
    $.map(unindexed_array, function(n, i){
        if(n['value'] !== '') {
            indexed_array[n['name']] = n['value'];
        }
	});
    
    return indexed_array;
}


function submitSavedFormsView(){
    if(navigator.onLine){
	var u_forms = getSavedEncounters();		
	if(u_forms === null) {
	    alert("There are no forms to process.");
	}
	else {	    
	    for(var key in u_forms) {
		var form_data = u_forms[key];                
		form_data["key"] = key;
		submitSavedEncounter(form_data);
	    }             
	}
    }
    else {
	alert('You are currently offline. You must be online to process saved forms');
    }                     
}


function patientSearchView() { 
    $(".app").hide();
    $("#patient_search_view").css("display","inline");
    $("#list_location_uuid").val("");
    $("#list_defaulter_cohort_id").val("");
    
    var s = $("#search_string").val();
    if(s.length > 3) {
	patientSearch(s,patientsToList);	
    }
}

function patientsToList(patients) {
    $("#patient_list").empty();    
    for(var i=0; i<patients.length;i++) {
	var row =  patients[i];        
	var html = "<li><a onClick=\"patientDashboardView('"+ row['uuid'] + "')\">";
	html += row['family_name'] + ", " + row['given_name'] + " " + row['middle_name'] + "<br/>";
	html += "Sex: " + row['gender'] + "; Birthdate: " + row['birthdate'] + "<br/>";
	html += "Identifier(s): " + row['identifier'];
	html += "</a></li>";
	$("#patient_list").append(html).listview("refresh");
    }
}

function updatePhoneNumberView() {
    var num = $("#patient_dashboard_view #dash_phone_number").val();
    var patient_uuid = $("#patient_dashboard_view #dash_patient_uuid").val();
    console.log("Updating phone number: " + num + " patient_uuid: " + patient_uuid);
    if(num.length != 10) {
	alert('This phone number has ' + num.length + ' digits. Phone number must be 10 digits and contain no spaces. For example: 0724123456.');
    }
    else {
	if(confirm('Are you sure you want to update this phone number to ' + num + '?')) {
	    updatePhoneNumber(patient_uuid,num);
	}
    }


}