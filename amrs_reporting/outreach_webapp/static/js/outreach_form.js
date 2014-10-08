

$(document).ready(function() {
	$("#contacted_by_phone").change(function () {
		if($("#contacted_by_phone option:selected").text().toLowerCase() === 'yes') {
		    $("#refer_for_field_follow_up").removeAttr('required').attr('disabled','disabled').val('');
		    $("#owner_of_phone").attr('required','required');
		}
		else if($("#contacted_by_phone option:selected").text().toLowerCase().match('^no')) {
		    $("#owner_of_phone").removeAttr('required');             
		    $("#refer_for_field_follow_up").removeAttr('disabled').attr('required','required').val('');
		}
		else {
		    $("#refer_for_field_follow_up").removeAttr('required').attr('disabled','disabled').val('');
		}
	    }).trigger('change');
	
	
	$("#contacted_in_field").change(function() {
		if($("#contacted_in_field option:selected").text().toLowerCase() === 'yes') {
		    $("#reason_not_found_in_field").attr('disabled','disabled').removeAttr('required').val('');
		    $("#date_found").val($("#encounter_datetime").val());
		}
		else if($("#contacted_in_field option:selected").text().toLowerCase() == 'no') {
		    $("#reason_not_found_in_field").attr('required','required').removeAttr('disabled');
		}
		else {
		    $("#refer_not_found_in_field").removeAttr('required').attr('disabled','disabled').val('');
		}
	    });


	$("#patient_status").change(function() {
		if($("#patient_status option:selected").text().toLowerCase().match('^patient wishes')) {
		    $("#return_visit_date").removeAttr('disabled');
		    $("#likelihood_of_return").removeAttr('disabled');
		}
		else {
		    $("#return_visit_date").attr('disabled','disabled').val('');
		    $("#likelihood_of_return").attr('disabled','disabled').val('');
		}
		
		if($("#patient_status option:selected").text().toLowerCase().match('to ampath')){
		    $("#transfer_location").removeAttr('disabled');
		}
		else {
		    $("#transfer_location").attr('disabled','disabled').val('');
		}
		
	    });
	
	$("#contacted_by_phone").change(function() {
		if($("#contacted_by_phone option:selected").text() == "Yes") {
		    $("#date_found").val($("#encounter_datetime").val());
		    $("#location_of_contact").val("a89de832-1350-11df-a1f1-0026b9348838");
		    $("#location_of_contact").selectmenu("refresh");
		}
		
	    });


	$("#tabs-1").show();
	$("#tabs-2").hide();
	$("#tabs-3").hide();
	$("#tabs-4").hide();
	$("#tabs-5").hide();
	
  
	$("#tabs-1-link").click(function() { 
		$("#tabs-1").show();
		$("#tabs-2").hide();
		$("#tabs-3").hide();
		$("#tabs-4").hide();
		$("#tabs-5").hide();
	    });
	

	$("#tabs-2-link").click(function() { 
		$("#tabs-2").show();
		$("#tabs-1").hide();
		$("#tabs-3").hide();
		$("#tabs-4").hide();
		$("#tabs-5").hide();
	    });


	$("#tabs-3-link").click(function() { 
		$("#tabs-3").show();
		$("#tabs-1").hide();
		$("#tabs-2").hide();
		$("#tabs-4").hide();
		$("#tabs-5").hide();
	    });


	$("#tabs-4-link").click(function() { 
		$("#tabs-4").show();
		$("#tabs-1").hide();
		$("#tabs-2").hide();
		$("#tabs-3").hide();
		$("#tabs-5").hide();
	    });


	$("#tabs-5-link").click(function() { 
		$("#tabs-5").show();
		$("#tabs-1").hide();
		$("#tabs-2").hide();
		$("#tabs-3").hide();
		$("#tabs-4").hide();
	    });
    

	var t = new Date();
	$("#encounter_datetime").val($.datepicker.formatDate('yy-mm-dd',new Date()));
	$("#encounter_datetime").datepicker({dateFormat:'yy-mm-dd'});
	$("#missed_return_visit_date").datepicker({dateFormat:'yy-mm-dd'});
	$("#date_found").datepicker({dateFormat:'yy-mm-dd'});
	$("#return_visit_date").datepicker({dateFormat:'yy-mm-dd'});
	$("#date_of_death").datepicker({dateFormat:'yy-mm-dd'});



}); //END Document.ready

  $("#outreach_form").validate();

  jQuery.validator.addMethod("needs_date_found", function(value, element) {
     if(value === '') {
        return ($("#contacted_in_field option:selected").text().toLowerCase() != 'yes'
               && $("#contacted_by_phone option:selected").text().toLowerCase() != 'yes');
     }
     else { return true; }
     }, "* Must provide date found"
  );


  jQuery.validator.addMethod("needs_location_of_contact", function(value, element) {
     if(value === '') {
        return ($("#contacted_in_field option:selected").text().toLowerCase() != 'yes'
               && $("#contacted_by_phone option:selected").text().toLowerCase() != 'yes')
               && $("#date_found").val() == ''
     }
     else { return true;}
     }, "* Must provide location of contact"
  );


  jQuery.validator.addMethod("needs_rtc_date", function(value, element) {
     if($("#patient_status option:selected").text().toLowerCase().match('^patient wishes')) {
        return value != '';
     }
     else { return true; }
     }, "* Must provide RTC date"
  );


  jQuery.validator.addMethod("needs_likelihood_of_return", function(value, element) {
     if($("#patient_status option:selected").text().toLowerCase().match('^patient wishes')) {
	 console.log("validate: needs_likelihood_of_return");
        return value != '';
     }
     else { return true; }
     }, "* Must provide likelihood of patient returning"
  );


  jQuery.validator.addMethod("needs_transfer_location", function(value, element) {
     if($("#patient_status option:selected").text().toLowerCase().match('to ampath')) {
        return value != '';
     }
     else { return true; }
     }, "* Must provide transfer location"
  );

  jQuery.validator.addMethod("needs_phone_number", function(value, element) {
     if($("#contacted_by_phone option:selected").text().toLowerCase() === 'yes') {
        return value != '';
     }
     else { return true; }
     }, "* Must provide phone number"
  );
  

  jQuery.validator.addMethod("needs_death_info", function(value, element) {
     if($("#patient_status option:selected").text().toLowerCase() === 'patient dead') {
        return value != '';
     }
     else { return true; }
     }, "* Must provide death date and cause for death"
  );

    jQuery.validator.addMethod("check_death_date", function(value, element) {
	    console.log("validator: checking death date");	    
	    var re = /^\d{4}-\d{2}-\d{2}$/;
	    // valid if optional and empty OR if it passes the regex test
	    return (this.optional(element) && value=="") || re.test(value);
	},
	function(params,element) { return 'Date is in invalid format. Please use YYYY-MM-DD';}
	);



