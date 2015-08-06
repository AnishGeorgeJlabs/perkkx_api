###
  Wadi sms tool web interface
###

angular.module("Wadi", [])
.config ($stateProvider) ->
  $stateProvider
    .state('home',
      url: "/home"
      abstract: true
      templateUrl: "index.html"
    )
