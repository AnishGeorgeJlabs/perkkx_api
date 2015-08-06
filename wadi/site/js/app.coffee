###
  Wadi sms tool web interface
###

angular.module("Wadi", [])
.controller 'MainCtrl', ($scope, $log) ->
  $scope.data = [
    {
      group: "Platform of Purchase"
      items: ["Desktop", "Mobile"]
    },
    {
      group: "Geography of Purchase"
      items: ["UAE", "KSA", "Others"]
    }
  ]

  formdata = {}
  submit = () ->
    data = JSON.stringify($("#dataForm").serializeArray())
    $log.info("Got form data: "+data)
