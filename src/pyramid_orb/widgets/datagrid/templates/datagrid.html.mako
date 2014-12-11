<table id="${widget.id()}" class="table table-striped table-bordered" width="100%">
    <thead>
        <tr>
            % for column in widget.columns():
            <th>${column.displayName()}</th>
            % endfor
        </tr>
    </thead>
</table>