$(document).ready(function(){
// get csrftoken first
var csrftoken = $('input').attr('value');
// on start button click
$('#startbtn').click(function(){
    $.ajax({
        headers:{"X-CSRFToken":csrftoken},
        data:'{"action":"start"}',
        method:"PUT",
    })
})
// on stop button click
$('#stopbtn').click(function(){
    $.ajax({
        headers:{"X-CSRFToken":csrftoken},
        data:'{"action":"stop"}',
        method:"PUT",
    })
})
// on delete button click
$('#deletebtn').click(function(){
    $.ajax({
        headers:{"X-CSRFToken":csrftoken},
        method:"DELETE"
    })
})
// filter used for tables (two if ther are two per page)
$('#filter_table').keyup(function () {
    var regexp = new RegExp($(this).val(), 'i');
    $('.filter_table tr').hide();
    $('.filter_table tr').filter(function () {
        return regexp.test($(this).text());
    }).show();
})

$('#filter_table_2').keyup(function () {
    var regexp = new RegExp($(this).val(), 'i');
    $('.filter_table_2 tr').hide();
    $('.filter_table_2 tr').filter(function () {
        return regexp.test($(this).text());
    }).show();
})

// filter used for rows (container and host list)
$('#filter_row').keyup(function () {
    var regexp = new RegExp($(this).val(), 'i');
    $('.filter_row div.row').hide();
    $('.filter_row div.row').filter(function () {
        return regexp.test($(this).text());
    }).show();
})


});
