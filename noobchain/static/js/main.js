function update_values() {
            $SCRIPT_ROOT = {{ request.script_root|tojson|safe }};
            $.getJSON($SCRIPT_ROOT+"/_stuff",
                function(data) {
                    $("#cpuload").text(data.cpu+" %")
                    $("#ram").text(data.ram+" %")
                    $("#disk").text(data.disk+" %")
                });
        }