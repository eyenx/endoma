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
});
