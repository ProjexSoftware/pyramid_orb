<script type="text/javascript">
    ;(function ($, window, document, undefined) {
        $.widget('bootstrap.queryBuilder', {
            // default options
            options : {
                rules: [],
                content_template: '\
                    <form class="form" role="form"> \
                        <div role="querybuilder"> \
                            <div class="row"> \
                                <div class="col-md-1"> \
                                    <button disabled type="button" class="btn btn-default remove-rule-btn"> \
                                        <i class="fa fa-remove"></i> \
                                    </button> \
                                </div> \
                                <div class="col-md-8"> \
                                    <div class="input-group" role="group"> \
                                        <select class="selectpicker" role="rule">\
                                            <option value="">Select...</option>\
                                        </select> \
                                        <select disabled class="selectpicker" role="operator" title="..."> \
                                        </select> \
                                        <input disabled class="form-control" type="text" role="editor"/> \
                                    </div> \
                                </div> \
                                <div class="col-md-3"> \
                                    <div class="btn-group btn-block" role="group"> \
                                        <button disabled type="button" class="btn btn-primary and-btn" style="width: 50%">And</button> \
                                        <button disabled type="button" class="btn btn-primary or-btn" style="width: 50%">Or</button> \
                                    </div> \
                                </div> \
                            </div>\
                        </div> \
                    </form>',
                rule_template: '\
                    <div class="spacer" style="min-height: 6px;"/>\
                    <div class="row"> \
                        <div class="col-md-1"> \
                            <button type="button" class="btn btn-default remove-rule-btn"> \
                                <i class="fa fa-remove"></i> \
                            </button> \
                        </div> \
                        <div class="col-md-8"> \
                            <div class="input-group" role="group"> \
                                <select class="selectpicker" role="rule"> \
                                    <option value="">Select...</option> \
                                </select> \
                                <select disabled class="selectpicker" role="operator" title="..."> \
                                </select> \
                                <input disabled class="form-control" type="text" role="editor"> \
                            </div> \
                        </div> \
                        <div class="col-md-3"> \
                            <div role="group"> \
                                <button disabled type="button" class="btn btn-block btn-primary and-or-btn">And</button> \
                            </div> \
                        </div> \
                    </div>'
            },

            // setup widget
            _init : function () {
                var self = this;
                var options = self.options;

                // create the popover
                var $element = $(self.element);
                $element.popover({
                    html: true,
                    placement: 'bottom',
                    content: options.content_template
                });

                // create the update for the popover
                $element.on('shown.bs.popover', function (event) {
                    $('[role="querybuilder"]').each(function () {
                        var $builder = $(this);
                        var $rule = $builder.find('[role="rule"]').first();

                        var options = "";
                        $.each(self.options.rules, function (key, rule) {
                            options += '<option value="' + key + '">' + rule.name + '</option>';
                        });
                        $rule.append(options);
                        $rule.selectpicker();
                        $rule.on('change', self.load_operators);

                        var $op = $builder.find('[role="operator"]');
                        $op.selectpicker();
                        $op.on('change', self.load_widget);

                        $builder.find('.and-btn').click(self.add_rule);
                        $builder.find('.or-btn').click(self.add_rule);
                        $builder.find('.remove-rule-btn').click(self.remove_rule);

                        var $popover = $builder.closest('.popover');
                        $popover.css('min-width', '700px');
                        $popover.css('max-width', '700px');

                    });
                });
            },

            _create : function () {
                var self = this;

                // create instance methods
                self.add_rule = function (event) {
                    var $title = $(event.target).text();
                    var $content = $(event.target).closest('[role="querybuilder"]');
                    var $source_row = $(event.target).closest('.row');

                    // only allow a new entry from the last item
                    if ($source_row.is($content.children().last())) {
                        // update all the optional buttons to the one clicked
                        $content.append(self.options.rule_template);

                        var $row = $content.children().last();
                        var $rule = $row.find('[role="rule"]').first();
                        var options = "";
                        $.each(self.options.rules, function (key, rule) {
                            options += '<option value="' + key + '">' + rule.name + '</option>';
                        });
                        $rule.append(options);
                        $rule.selectpicker();
                        $rule.on('change', self.load_operators);

                        // create connections
                        var $op = $row.find('[role="operator"]').first();
                        $op.selectpicker();
                        $op.on('change', self.load_widget);

                        $row.find('.and-or-btn').click(self.add_rule);
                        $row.find('.remove-rule-btn').click(self.remove_rule);
                    }

                    $content.find('.and-or-btn').text($title);
                    $content.find('.and-or-btn').addClass('active');
                    if ( $title == 'And' ) {
                        $content.find('.and-btn').addClass('active');
                        $content.find('.or-btn').removeClass('active');
                    } else {
                        $content.find('.and-btn').removeClass('active');
                        $content.find('.or-btn').addClass('active');
                    }
                };

                self._load_widget = function ($operator) {
                    var $container = $operator.closest('.row');
                    var $rule = $container.find('[role="rule"]').first();

                    var rule = self.options.rules[$rule.val()];
                    var op = rule ? rule.operators[$operator.val()] : null;

                    var $editor = $container.find('[role="editor"]').first();
                    var $inputs = $editor.parent();
                    var curr_val = $editor.val();
                    var disabled = $editor.prop('disabled');

                    $editor.remove();

                    if ( !(op && op.widget) ) {
                        $inputs.append('<input type="text" class="form-control">');
                        $editor = $inputs.children().last();
                    } else {
                        $inputs.append(op.widget);
                        $editor = $inputs.children().last();
                    }
                    if ( op && op.widget ) {
                        op.init($editor);
                    }

                    $editor.val(disabled ? '' : curr_val);
                    $editor.prop('disabled', disabled);
                    $editor.attr('role', 'editor');
                };

                self._load_operators = function ($rule) {
                    var $container = $rule.closest('.row');
                    var disabled = $rule.val() == "";
                    var $op = $container.find('[role="operator"]').first();
                    var $editor = $container.find('[role="editor"]').first();

                    $op.prop('disabled', disabled);
                    $editor.prop('disabled', disabled);
                    $container.find('.remove-rule-btn').prop('disabled', disabled);
                    $container.find('.and-btn').prop('disabled', disabled);
                    $container.find('.or-btn').prop('disabled', disabled);
                    $container.find('.and-or-btn').prop('disabled', disabled);

                    if ( disabled ) {
                        $op.empty();
                    }
                    else {
                        var rule = self.options.rules[$rule.val()];
                        var options = "";
                        var first_op = null;
                        $.each(rule.operators, function (key, op) {
                            if ( first_op == null ) { first_op = op; }
                            options += '<option value="' + key + '">' + op.name + '</option>';
                        });

                        $op.html(options);
                    }

                    $op.selectpicker('refresh');
                    self._load_widget($op);
                };

                self.load_widget = function (event) { self._load_widget($(event.target)); };
                self.load_operators = function (event) { self._load_operators($(event.target)); };

                self.remove_rule = function (event) {
                    var $button = $(event.target);
                    var $container = $button.closest('[role="querybuilder"]');

                    if ($container.children().length > 1) {
                        $container.children().last().remove();
                        $container.children().last().remove();
                    } else {
                        $container.find('.and-btn').removeClass('active');
                        $container.find('.or-btn').removeClass('active');
                        var $rule = $container.find('[role="rule"]').first();

                        $rule.val('');
                        $rule.selectpicker('refresh');
                        self._load_operators($rule);
                    }
                };
            },

            // destroy the widget
            destroy : function () {
                $.Widget.prototype.destroy.call(this);
            }
        });
    })(jQuery, window, document);

    $(document).ready(function () {
        var options = {
            rules: {
                displayName: {
                    name: 'Display name',
                    operators: {
                        is: {
                            name: 'is'
                        },
                        is_not: {
                            name: 'is not'
                        }
                    }
                },
                email: {
                    name: 'Email',
                    operators: {
                        is: {
                            name: 'is'
                        },
                        is_not: {
                            name: 'is not'
                        },
                        is_in: {
                            name: 'is in'
                        },
                        is_none: {
                            name: 'is none',
                            widget: '<input type="hidden">'
                        },
                        is_not_none: {
                            name: 'is not none',
                            widget: '<input type="hidden">'
                        }
                    }
                },
                created_at: {
                    name: 'Created',
                    operators: {
                        before: {
                            name: 'before',
                            widget: '<input class="form-control datepicker" data-date-format="mm/dd/yyyy">',
                            init: function ($editor) {
                                $editor.datepicker();
                            }
                        },
                        after: {
                            name: 'after',
                            widget: '<input class="form-control datepicker" data-date-format="mm/dd/yyyy">',
                            init: function ($editor) {
                                $editor.datepicker();
                            }
                        }
                    }
                }
            }
        };
        $('[data-toggle="querybuilder"]').queryBuilder(options);
    });
</script>