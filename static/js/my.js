        $(document).ready(function() {

            var HelloButton = function (context) {
              var ui = $.summernote.ui;
              var button = ui.button({
                contents: '<span class="glyphicon glyphicon-calendar"></span>',
                tooltip: 'hello',
                click: function () {
                  context.invoke('editor.insertText', 'hello');
                }
              });
              return button.render();
            };

            $('#datepicker').datetimepicker({
                locale: 'ru',
                format: 'YYYY-MM-DD HH:mm:ss'
            });

            $.ajaxSetup({
                beforeSend: function(xhr, settings) {
                    if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", csrftoken)
                    }
                }
            });

            var cfg = {
                height: 170,
                callbacks: {
                    onImageUpload: function (files) {
                        var note = $(this);
                        sendFile(files[0], note);
                    }
                },
                toolbar: [
                    ['style', ['style']],
                    ['font', ['bold', 'underline', 'clear']],
                    ['color', ['color']],
                    ['para', ['ul', 'ol', 'paragraph']],
                    ['table', ['table']],
                    ['insert', ['link', 'picture', 'video']],
                    ['view', ['codeview', 'help']],
                    ['mybutton', ['hello']]
                ],
                buttons: {
                    hello: HelloButton
                }
            };

            function sendFile(file, note) {
                var data = new FormData();
                data.append("file", file);
                $.ajax({
                    data: data,
                    type: "POST",
                    url: "/upload",
                    cache: false,
                    contentType: false,
                    processData: false,
                    success: function(url) {
                        note.summernote('insertImage', url, function ($image) {
                            $image.attr('class', 'pull-left');
                            $image.removeAttr('style');
                        })
                    }
                });
            };

            $('#intro').summernote(cfg);
            cfg.height = 400;
            $('#text').summernote(cfg);

        });
