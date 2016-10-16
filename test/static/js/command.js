/**
 * Created by Agustin Antoine on 11-10-2016.
 */

function stop_performed(output, server_id) {
    var start_id = '#button_start'+server_id;
    var stop_id = '#button_stop'+server_id;
    var restart_id = '#button_restart'+server_id;
    var img_id = '#img'+server_id;
    if (output === "success") {
        $(start_id).removeAttr("disabled");
        $(stop_id).attr("disabled", "disabled");
        $(restart_id).attr("disabled", "disabled");
        $(img_id).attr("src", "/static/img/offline.png");

        $('div#body').prepend(
            "<div id='alert' class='alert alert-success' >" +
                "Server stopped correctly!" +
            "</div>");
    } else if (output === "warning") {
        $('div#body').prepend(
            "<div id='alert' class='alert alert-warning' >" +
                "Server was already stopped!" +
            "</div>");
    } else {
        $('div#body').prepend(
            "<div id='alert' class='alert alert-danger' >" +
                "Server could not be stopped!" +
            "</div>");
    }
}

function restart_performed(output, server_id) {
    var start_id = '#button_start'+server_id;
    var stop_id = '#button_stop'+server_id;
    var restart_id = '#button_restart'+server_id;
    var img_id = '#img'+server_id;
    if (output === "success") {
        $('div#body').prepend(
            "<div id='alert' class='alert alert-success' >" +
                "Server stopped correctly!" +
            "</div>");
    } else {
        $(start_id).removeAttr("disabled");
        $(stop_id).attr("disabled", "disabled");
        $(restart_id).attr("disabled", "disabled");
        $(img_id).attr("src", "/static/img/offline.png");
        if (output === "warning") {
            $('div#body').prepend(
                "<div id='alert' class='alert alert-warning' >" +
                "Server was stopped, can not restart!" +
                "</div>");
        } else {
            $('div#body').prepend(
                "<div id='alert' class='alert alert-danger' >" +
                "Server could not be restarted!" +
                "</div>");
        }
    }
}


function start_performed(output, server_id) {
    var start_id = '#button_start'+server_id;
    var stop_id = '#button_stop'+server_id;
    var restart_id = '#button_restart'+server_id;
    var img_id = '#img'+server_id;
    if (output === "success") {
        $(start_id).attr("disabled", "disabled");
        $(stop_id).removeAttr("disabled");
        $(restart_id).removeAttr("disabled");
        $(img_id).attr("src", "/static/img/online.png");

        $('div#body').prepend(
            "<div id='alert' class='alert alert-success' >" +
                "Server started correctly!" +
            "</div>");
    } else if (output === "warning") {
        $('div#body').prepend(
            "<div id='alert' class='alert alert-warning' >" +
                "Server was already running!" +
            "</div>");
    } else {
        $('div#body').prepend(
            "<div id='alert' class='alert alert-danger' >" +
                "Server could not be started!" +
            "</div>");
    }
}

function set_button_status(command, server_id, output) {
    if (command === "start") {
        start_performed(output, server_id)
    } else if (command === "stop") {
        stop_performed(output, server_id)
    } else if (command === "restart") {
        restart_performed(output, server_id)
    }
}

function command_exec(command, action, server_id) {
    $('div#alert').remove();
    $.getJSON($SCRIPT_ROOT + '/command/'+command+'/'+server_id, {
    }, function(data) {
        $('div#alert').remove();
        set_button_status(command, server_id, data.output);
        /*alert(data.output);*/
    });
    $('div#body').prepend(
        "<div id='alert' class='alert alert-warning' " +
            "<p><img src='/static/img/ajax-loader.gif'>" +
            "&nbsp;&nbsp; "+action+" server... This may take a while</p>" +
        "</div>");
    return false;
}