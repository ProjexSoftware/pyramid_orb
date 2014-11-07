<table id="${grid.id()}" class="table table-striped table-bordered" width="100%">
    <thead>
        <tr>
            % for column in grid.columns():
            <th>${column.displayName()}</th>
            % endfor
        </tr>
    </thead>
</table>