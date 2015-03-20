<script type="text/javascript">
    ;(function ($, window, document, undefined) {
        var pluginName = 'queryBuilder';
        var defaults = {
            rules : [],
            content_template : '\
                <form class="form querybuilder" role="form"> \
                    <div class="row"> \
                        <div class="col-md-1"> \
                            <button type="button" class="btn btn-default remove-rule-btn"> \
                                <i class="fa fa-remove"></i> \
                            </button> \
                        </div> \
                        <div class="col-md-8"> \
                            <div class="input-group" role="group"> \
                                <select class="selectpicker" role="rule"></select> \
                                <select class="selectpicker" role="operator"></select> \
                                <input class="form-control" type="text" role="value"/> \
                            </div> \
                        </div> \
                        <div class="col-md-3"> \
                            <div class="btn-group" role="group"> \
                                <button type="button" class="btn btn-primary and-btn">And</button> \
                                <button type="button" class="btn btn-primary or-btn">Or</button> \
                            </div> \
                        </div> \
                    </div> \
                </form>',
            rule_template : '\
                    <div class="row"> \
                        <div class="col-md-1"> \
                            <button type="button" class="btn btn-default remove-rule-btn"> \
                                <i class="fa fa-remove"></i> \
                            </button> \
                        </div> \
                        <div class="col-md-8"> \
                            <div class="input-group" role="group"> \
                                <select class="selectpicker" role="rule"> \
                                </select> \
                                <select class="selectpicker" role="operator"> \
                                </select> \
                                <input class="form-control" type="text"> \
                            </div> \
                        </div> \
                        <div class="col-md-3"> \
                            <div role="group"> \
                                <button type="button" class="btn btn-block btn-primary and-or-btn">And</button> \
                            </div> \
                        </div> \
                    </div>'
        };

        function QueryBuilder(element, options) {
            this.element = element;

            this.options = $.extend({}, defaults, options);
            this._defaults = defaults;
            this._name = pluginName;

            // define the local method scope
            this.add_rule = function (event) {
                var $title = $(event.target).text();

                var $content = $(event.target).closest('.popover-content');
                $content.append(this.options.rule_template);
                var $new_rule = $content.children().last();

                // create connections
                $new_rule.find('.selectpicker').selectpicker();
                $new_rule.find('.and-or-btn').click(this.add_rule);
                $new_rule.find('.remove-rule-btn').click(this.remove_rule);

                // update all the optional buttons to the one clicked
                $('.and-or-btn').text($title);
            };

            this.remove_rule = function (event) {
                $(event.target).closest('.row').remove();
            };

            this.init();
        }

        QueryBuilder.prototype.init = function () {
            var $element = $(this.element);

            $element.popover({
                html: true,
                placement: 'bottom',
                content: this.options.content_template
            });

            $element.on('shown.bs.popover', function (event) {
                var $self = $(event.target).queryBuilder();
                console.log($self);
                console.log($self.add_rule);
                $('.querybuilder').each(function () {
                    var $node = $(this);

                    $node.find('.selectpicker').selectpicker();
                    $node.find('.and-btn').click(this.add_rule);
                    $node.find('.or-btn').click(this.add_rule);
                    $node.find('.remove-rule-btn').click(this.remove_rule);
                    $node.closest('.popover').css('maxWidth', '700px');
                });
            });
        };

        $.fn[pluginName] = function (options) {
            return this.each(function () {
                if (!$.data(this, 'plugin_' + pluginName)) {
                    $.data(this, 'plugin_' + pluginName,
                            new QueryBuilder(this, options));
                }
            });
        };

        // automatically load data for the builder objects
        $(document).ready(function () {
            var $rules = [
                {
                    name : 'Display Name',
                    value : 'displayName',
                    operators : [
                        {
                            name : 'Is',
                            value : 'is',
                            widget : 'text'
                        },
                        {
                            name : 'Is Not',
                            value : 'is_not',
                            widget : 'text'
                        },
                        {
                            name : 'Is None',
                            value : 'is_none',
                            widget : null
                        },
                        {
                            name : 'Is Not None',
                            value : 'is_not_none',
                            widget : null
                        }
                    ]
                }
            ];
            $('[data-toggle="querybuilder"]').queryBuilder({rules : $rules});
        });

    })(jQuery, window, document);

</script>