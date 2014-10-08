
function appsView() {
    $(".app").hide()
	$("#apps_view").css("display","inline");
}



function defaulterCohortListView(){
    $(".app").hide();
    var cur_list_id = $("#list_defaulter_cohort_id").val();
    var id = $("#defaulter_cohort").val();
    if((id !== "") && ((id != cur_list_id) || ($("#defaulter_cohort_list li").length == 0)))  {
	var cohort = getCohort(id);
	$("#defaulter_cohort_list_view #defaulter_cohort_name").text(cohort["name"]);
	$("#defaulter_cohort_list_view #date_created").text(cohort["date_created"]);
	defaulterCohortToList(cohort);
    }      
    $("#defaulter_cohort_list_view").css("display","inline");
}



//key : defaulter_cohort_id_NN
function defaulterCohortToList(cohort) {			    
    $("#defaulter_cohort_list").empty();
    var patients = cohort["patients"];
    var key = "defaulter_cohort_id_" + cohort["id"];
    var total_patients = Object.keys(patients).length; 
    var num_remaining = total_patients;
    for(var uuid in patients) {           
	var row = patients[uuid];
	var s = "<li";
	if(row['retired']) {
	    s += " class='retired'";
	    num_remaining = num_remaining - 1;
	}
	s += "><a onClick=\"patientDashboardView('" + row["patient_uuid"] + "')\">";
	s += row["family_name"] + ", " + row["given_name"] + " " + row["middle_name"] + "<br/>";
	s += row["identifier"] + "<br/>";
            s += "Phone: " + row["phone_number"];
            $("#defaulter_cohort_list").append(s).listview("refresh");    	  
    }
    $("#list_location_uuid").val(cohort["location_uuid"]);
    
    var id = cohort["id"];
    $("#list_defaulter_cohort_id").val(id);
    $("#defaulter_cohort_list_view #num_remaining").text("Patients remaining to be traced: " + num_remaining + " / " + total_patients);        
}


function patientDashboardView(patient_uuid) {
    $(".app").hide();
    $("#patient_dashboard_view").css("display","inline");
    
    var cohort_id = $("#list_defaulter_cohort_id").val();
    var patient = getPatient(cohort_id,patient_uuid);

    console.log("Patient Info: " + JSON.stringify(patient));
    $("#dash_patient_name").text(patient["given_name"] + " " + patient["middle_name"] + " " + patient["family_name"]);
    $("#dash_identifier").text(patient["identifier"]);
    $("#dash_birthdate").text(patient["birthdate"].substring(0,10));
    $("#dash_phone_number").val(patient["phone_number"]);
    $("#dash_patient_uuid").val(patient["patient_uuid"]);
}



function outreachFormView(){
    $(".app").hide();
    $("#outreach_form_view").css("display","inline");	

    var cohort_id = $("#list_defaulter_cohort_id").val();    
    var patient_uuid = $("#dash_patient_uuid").val();
    var patient = getPatient(cohort_id,patient_uuid);

    console.log(patient);
        
    $("#return_to_dashboard").attr("onClick","viewPatientDashboard('" + patient["patient_uuid"] + "')");

    $("#outreach_form_view input[auto-populate='True']").each(function(index) {
	    $(this).attr("value",(patient[$(this).attr("id")])); 
	});
    
    $("#outreach_form #location_uuid").val($("#list_location_uuid").val());
    $("#outreach_form #defaulter_cohort_id").val($("#list_defaulter_cohort_id").val());
    
    var t = new Date();
    $("#encounter_datetime").val($.datepicker.formatDate('yy-mm-dd',new Date())); 
    $("#encounter_datetime").datepicker({dateFormat:'yy-mm-dd'});    
}    



function submitOutreachFormView() {
    if($("#outreach_form").valid()) {
        var d = getFormData($("#outreach_form"));
	submitEncounter(d);
        $("#outreach_form").trigger("reset");        
        var id = $("#outreach_form #defaulter_cohort_id").val();
        var patient_uuid = $("#outreach_form #patient_uuid").val();
        retirePatient(id,patient_uuid);
        $("#defaulter_cohort_list").empty();
        return false;
    } else {
	alert("This form has errors. Please correct them before submitting");
	return true;
    }
}


function retirePatient(cohort_id,patient_uuid) {
    var cohort = getCohort(cohort_id)
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
