###
  Wadi sms tool web interface
###

staticData = [
  {
    group: "Language"
    items: ["Arabic", "English"]
  },
  {
    group: "Platform of Purchase"
    items: ["Desktop", "Mobile"]
  },
  {
    group: "Geography of Purchase"
    items: ["UAE", "KSA", "Others"]
  },
  {
    group: "Channel of Purchase"
    items: ["Last touch click", "Direct", "Newsletter"]
  },
  {
    group: "Payment Method"
    items: ["Inovative", "Postpayment"]
  },
  {
    group: "Number of items purchased"
    items: ['1', '1-2', '2-3', '3+']
  }
]

angular.module("Wadi", [])
.controller 'MainCtrl', ($scope, $log, $http) ->
  $scope.data = staticData

  $scope.formdata = {}
  $scope.submit = () ->
    nData = $("#dataForm").serializeObject()
    $log.info("Object mode: "+JSON.stringify(nData))
    $http.post "http://45.55.72.208/wadi/post", nData
    .success (res) ->
      $log.info "Got result: "+JSON.stringify(res)
