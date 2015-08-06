###
  Wadi sms tool web interface
###

angular.module("Wadi", [])
.controller 'MainCtrl', ($scope) ->
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
