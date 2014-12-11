<script type="text/javascript">
    $(document).ready(function() {
        var helper = undefined;
        var breakpointDefinition = {
            tablet : 1024,
            phone : 480
        };

        var otable = $('#${widget.id()}').DataTable({
            "autoWidth" : true,
            "preDrawCallback" : function() {
                // Initialize the responsive datatables helper once.
                if (!helper) { helper = new ResponsiveDatatablesHelper($('#${widget.id()}'), breakpointDefinition); }
            },
            "rowCallback" : function(nRow) { helper.createExpandIcon(nRow); },
            "drawCallback" : function(oSettings) { helper.respond(); },
            "ajax": function (data, callback, settings) {
                $.ajax({
                    url: "${widget.datasource()}",
                    success: function (data, status, xhr) {
                        callback({data: data});
                    }
                });
            },
            "columns": [
            % for column in widget.columns():
                {"data": "${column.fieldName()}"},
            % endfor
            ],
            ${config|n}
        });

        // Apply the filter
        $("#datatable thead th input[type=text]").on('keyup change', function () {
            otable
                .column( $(this).parent().index()+':visible' )
                .search( this.value )
                .draw();
        });
    });
</script>