(function() {

  ko.bindingHandlers.foreachprop = {
    transformObject: function(obj) {
      var properties = [];
      for (var key in obj) {
        if (obj.hasOwnProperty(key)) {
          properties.push({
            key: key,
            value: obj[key]
          });
        }
      }
      return properties;
    },
    init: function(
          element,
          valueAccessor, allBindingsAccessor,
          viewModel, bindingContext
    ) {
      var value = ko.utils.unwrapObservable(valueAccessor()),
        properties = ko.bindingHandlers.foreachprop.transformObject(value);
      ko.applyBindingsToNode(element, {
        foreach: properties
      });
      return {
        controlsDescendantBindings: true
      };
    }
  };

  function cleanHexStr(str) {
    return str.replace(/^#/, '');
  }

  function strToHex(str) {
    return parseInt(cleanHexStr(str), 16);
  }

  var ViewModel = function() {
    var self = this;

    self.colors = {
      bg: ko.observable('#c7c9c2'),
      fg: ko.observable('#0e0021'),
      menu_bg: ko.observable('#0e0021'),
      menu_fg: ko.observable('#888a85'),
      sel_bg: ko.observable('#1a617a'),
      sel_fg: ko.observable('#e6e6e6'),
      txt_bg: ko.observable('#c0bbbb'),
      txt_fg: ko.observable('#000000'),
      btn_bg: ko.observable('#77a8a5'),
      btn_fg: ko.observable('#0e0021')
    };

    self.border_color = ko.computed(function() {
      var borderColor = strToHex(self.colors.bg()) - 0x222222;
      if (borderColor <= 0) {
        return '#000000' }
      else {
        return '#' + borderColor.toString(16);
      };
    });

    self.output = ko.computed(function() {
      return 'NAME="custom"\n' +
        $.map(
          self.colors,
          function(value, key) {
            return key.toUpperCase() + '=' + cleanHexStr(value());
          }
        ).join('\n');
    });

  };

  ko.applyBindings(new ViewModel());

})();
