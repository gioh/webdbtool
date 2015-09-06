$(function() {
  $('#sidebar').on('click', '[data-toggle=collapse]', function() {
    var _$this        = $(this),
        _$nearestLi   = _$this.parent('li'), // The nearest <li> element
        _$submenu     = _$this.siblings('ul.nav'),
        _$parmenu     = _$this.closest('ul.nav');

    //** 当前状态
    var hasOpened     = _$nearestLi.hasClass('opened'),
        hasActivated = _$nearestLi.hasClass('activated');

    if (hasOpened) {
      _$submenu.slideUp(300, function () {
        _$nearestLi.removeClass('opened');
      });
      return;
    }

    //** !hasOpened && other has opened
    if (_$parmenu.children('.opened').length !== 0) {
      _$parmenu
        .children('.opened')
        .children('ul.nav')
        .slideUp(300, function () {
          $(this).parent().removeClass('opened');
        });
    }

    _$submenu.slideDown(300, function () {
      _$nearestLi.addClass('opened');
    });
  });
});