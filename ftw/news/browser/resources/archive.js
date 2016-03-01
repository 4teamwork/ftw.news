/*
  This javascript file provides accessibility support for the archive portlet.

  Controls on the year layer:

  Right arrow: Opens the current selected year and selects the first month.
  Left arrow: Closes the current opened year.
  Down arrow: Selects the next year in the year list.
  Up arrow: Selects the previous year in the year list.
  Enter: Opens the current selected year and selects the first month.

  Controls on the month layer:

  Down arrow: Selects the next month in the month list.
  Up arrow: Selects the previous month in the month list.
  Left arrow: Closes the opened year and select the year.
  Escape: Closes the opened year and select the year.

 */

(function() {

  "use strict";

  var element = $();

  function openYear(year) { year.addClass("expanded"); }

  function closeMonth(year) {
    $(".months", year.parent()).attr("aria-hidden", "true");
  }

  function closeYear(year) {
    year.removeClass("expanded");
    closeMonth(year);
    year.focus();
  }

  function toggleYear(year) {
    year.toggleClass("expanded");
    if(!year.hasClass("expanded")) {
      year.focus();
    }
  }

  function selectFirstMonth(year) {
    $(".month", year.parent()).first().focus();
    $(".months", year.parent()).attr("aria-hidden", "false");
  }

  var yearCarousel = {
    currentIndex: 0,
    years: $(".year"),
    next: function() {
      if(this.currentIndex === this.years.length - 1) {
        this.currentIndex = 0;
      } else {
        this.currentIndex ++;
      }
      this.focus();
    },
    previous: function() {
      if(this.currentIndex === 0) {
        this.currentIndex = this.years.length - 1;
      } else {
        this.currentIndex --;
      }
      this.focus();
    },
    focus: function() {
      this.years.eq(this.currentIndex).focus();
    },
    init: function(context) {
      this.years = $(".year", context);
      this.currentIndex = 0;
    }
  };

  var monthCarousel = {
    currentIndex: 0,
    months: $(),
    year: $(),
    next: function() {
      if(this.currentIndex === this.months.length - 1) {
        this.currentIndex = 0;
      } else {
        this.currentIndex ++;
      }
      this.focus();
    },
    previous: function() {
      if(this.currentIndex === 0) {
        this.currentIndex = this.months.length - 1;
      } else {
        this.currentIndex --;
      }
      this.focus();
    },
    focus: function() {
      this.months.eq(this.currentIndex).focus();
    },
    closeYear: function() {
      closeYear(this.year);
    },
    init: function(year, index) {
      this.year = year;
      this.months = $(".month", this.year.parent());
      this.currentIndex = index || 0;
    }
  };

  $(document).on("click", ".year", function(event) {
    event.preventDefault();
    toggleYear($(event.currentTarget));
  });

  $(document).on("keydown", ".year", function(event) {
    var year = $(event.currentTarget);
    monthCarousel.init(year);

    switch (event.which) {
      case $.ui.keyCode.RIGHT:
        event.preventDefault();
        openYear(year);
        selectFirstMonth(year);
        break;
      case $.ui.keyCode.LEFT:
        event.preventDefault();
        closeYear(year);
        break;
      case $.ui.keyCode.DOWN:
        event.preventDefault();
        yearCarousel.next();
        break;
      case $.ui.keyCode.UP:
        event.preventDefault();
        yearCarousel.previous();
        break;
      case $.ui.keyCode.ENTER:
        event.preventDefault();
        openYear(year);
        selectFirstMonth(year);
        break;
    }
  });

  $(document).on("keydown", ".month", function(event) {
    var month = $(event.currentTarget);

    switch (event.which) {
      case $.ui.keyCode.DOWN:
        event.preventDefault();
        monthCarousel.next(month);
        break;
      case $.ui.keyCode.UP:
        event.preventDefault();
        monthCarousel.previous(month);
        break;
      case $.ui.keyCode.LEFT:
        event.preventDefault();
        monthCarousel.closeYear();
        break;
      case $.ui.keyCode.ESCAPE:
        event.preventDefault();
        monthCarousel.closeYear();
        break;
    }
  });

  $(document).on("keyup", ".month", function(event) {
    var month = $(event.currentTarget);

    switch (event.which) {
      case $.ui.keyCode.TAB:
        monthCarousel.init(month.parents('.months').prev(), month.parent().index());
        break;
    }
  });

  $(function() {
    element = $(".archive-portlet");
    yearCarousel.init(element);
  });

}(window));
