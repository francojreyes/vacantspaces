var dynamicTable = (function () {

  var _tableId, _table,
      _fields, _headers,
      _defaultText;

  /** Builds the row with columns from the specified names.
   *  If the item parameter is specified, the memebers of the names array will be used as property names of the item; otherwise they will be directly parsed as text.
   */
  function _buildRowColumns(names, item) {
      var row = '<tr>';
      if (names && names.length > 0) {
          $.each(names, function (index, name) {
              var c = item ? item[name + ''] : name;
              row += (index == 0) ? '<td style="width:60%">': '<td>';
              row += c + '</td>';
          });
      }
      row += '</tr>';
      return row;
  }

  /** Builds and sets the headers of the table. */
  function _setHeaders() {
      // if no headers specified, we will use the fields as headers.
      _headers = (_headers == null || _headers.length < 1) ? _fields : _headers;
      var h = _buildRowColumns(_headers);
      if (_table.children('thead').length < 1) _table.prepend('<thead></thead>');
      _table.children('thead').html(h);
  }

  function _setNoItemsInfo() {
      if (_table.length < 1) return; //not configured.
      var colspan = _headers != null && _headers.length > 0 ?
          'colspan="' + _headers.length + '"' : '';
      var content = '<tr class="no-items"><td ' + colspan + ' style="text-align:center">' +
          _defaultText + '</td></tr>';
      if (_table.children('tbody').length > 0)
          _table.children('tbody').html(content);
      else _table.append('<tbody>' + content + '</tbody>');
  }

  function _removeNoItemsInfo() {
      var c = _table.children('tbody').children('tr');
      if (c.length == 1 && c.hasClass('no-items')) _table.children('tbody').empty();
  }

  return {
      /** Configres the dynamic table. */
      config: function (tableId, fields, headers, defaultText) {
          _tableId = tableId;
          _table = $('#' + tableId);
          _fields = fields || null;
          _headers = headers || null;
          _defaultText = defaultText || 'No items to list...';
          _setHeaders();
          _setNoItemsInfo();
          return this;
      },
      /** Loads the specified data to the table body. */
      load: function (data, append) {
          if (_table.length < 1) return; //not configured.
          _setHeaders();
          _removeNoItemsInfo();
          if (data && data.length > 0) {
              var rows = '';
              $.each(data, function (index, item) {
                  rows += _buildRowColumns(_fields, item);
              });
              var mthd = append ? 'append' : 'html';
              _table.children('tbody')[mthd](rows);
          } else {
              _setNoItemsInfo();
          }
          return this;
      },
      /** Clears the table body. */
      clear: function () {
          _setNoItemsInfo();
          return this;
      }
  };
}());

function update_weeks() {
  const weeks_by_term = {
      'Summer': ['1', '2', '3', '4', '5'],
      'T1': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'],
      'T2': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'],
      'T3': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
  };

  var term = document.getElementById("term").value;
  var weeks = document.getElementById("week")

  // Clear the list
  var i, L = weeks.options.length - 1;
  for (i = L; i >= 0; i--) {
      weeks.remove(i);
  }

  // Update it with new value of weeks
  for (const value of weeks_by_term[term]) {
      var opt = document.createElement('option');
      opt.value = value;
      opt.innerHTML = value;
      weeks.appendChild(opt);
  }
}

$(document).ready(function (e) {
  var dt = dynamicTable.config('data-table',
      ['room', 'from', 'to'],
      ['Room', 'Vacant From', 'Vacant Until'], //set to null for field names instead of custom header names
      'There are no items to list...');

  $("#btn-update").click(function (e) {
      // Create endpoint URL using select fields
      let url = 'http://localhost:5000/vacantspaces';
      url += '?term=' + document.getElementById("term").value;
      url += '&week=' + document.getElementById("week").value;
      url += '&day=' + document.getElementById("day").value;
      url += '&time=' + document.getElementById("time").value;
      url += '&campus=' + document.getElementById("campus").value;

      fetch(url)
          .then(function (response) {
              // Render the Response Status
              // Parse the body as JSON
              return response.json();
          })
          .then(function (json) {
              // Render the parsed body
              dt.load(json.data);
          })
  })

  $("#btn-now").click(function (e) {
      // Create endpoint URL using select fields
      let url = 'http://localhost:5000/vacantspaces/now';
      url += '?campus=' + document.getElementById("campus").value;

      fetch(url)
          .then(function (response) {
              // Render the Response Status
              // Parse the body as JSON
              return response.json();
          })
          .then(function (json) {
              console.log(json.data)
              // Render the parsed body
              dt.load(json.data);
          })
  })
});
