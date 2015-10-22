/*
File: custom.js
Comment: Custom JQUERY Javascript functions used in the endoma webapp
Project: EnDoMa
Author: Antonio Tauro
*/
$(document).ready(function(){
// get csrftoken first
var csrftoken = $('input').attr('value');
// on start button click
$('#startbtn').click(function(){
    // put data
    $.ajax({
        headers:{'X-CSRFToken':csrftoken},
        data:'{"action":"start"}',
        method:'PUT',
    });
    // go back to dashboard
    window.history.back();
});
// on stop button click
$('#stopbtn').click(function(){
    // put data
    $.ajax({
        headers:{'X-CSRFToken':csrftoken},
        data:'{"action":"stop"}',
        method:'PUT',
    });
    // go back to dashboard
    window.history.back();
});
// on delete button click
$('#deletebtn').click(function(){
    // put data
    $.ajax({
        headers:{'X-CSRFToken':csrftoken},
        method:'DELETE'
    });
    // go back to dashboard
    window.history.back();
});
// filter used for tables
$('#filter_table').keyup(function () {
    // create regex pattern
    var regexp = new RegExp($(this).val(), 'i');
    // hide all tablerows
    $('.filter_table tr').hide();
    // show only those who match the regexp
    $('.filter_table tr').filter(function () {
        return regexp.test($(this).text());
    }).show();
});

// filter used for tables  (for seconds table)
$('#filter_table_2').keyup(function () {
    // create regex pattern
    var regexp = new RegExp($(this).val(), 'i');
    // hide all tablerows
    $('.filter_table_2 tr').hide();
    // show only those who match the regexp
    $('.filter_table_2 tr').filter(function () {
        return regexp.test($(this).text());
    }).show();
});

// filter used for rows (container and host list)
$('#filter_row').keyup(function () {
    // create regex pattern
    var regexp = new RegExp($(this).val(), 'i');
    // hide all rows
    $('.filter_row div.row').hide();
    // show only matched rows
    $('.filter_row div.row').filter(function () {
        return regexp.test($(this).text());
    }).show();
});

// Dropdown functionality for container adding
// on change of selected host
$('#inputHost').change(function(){
    // empty the dropdown of conatainers
    $('#inputLink').html('');
    // append hidden values into dropdown menu
    $('#inputLink').append($('#availableContainers_'+$('#inputHost').val()).html());
});
// Links functionality add to hidden input field
// on click
$('#addLink').click(function(){
    // get selected
    var selected='<p>'+$('#inputLink :selected').text()+'</p>';
    // append this to the list
    $('#chosenLinksList').append(selected);
    // append this to the hidden input field
   	$('#chosenLinks').val($('#chosenLinks').val()+$('#inputLink').val()+',');
});
// Vars functionality add to hidden input field
// on click
$('#addVariable').click(function(){
    // get chosen environmentvariable
    var selected='<p>'+$('#inputKey').val()+' : '+$('#inputValue').val()+'</p>';
    // append this to the list
   $('#chosenVariablesList').append(selected);
   // append this to the hidden function
   $('#chosenVariables').val($('#chosenVariables').val()+$('#inputKey').val()+':'+$('#inputValue').val()+',');
});
});
