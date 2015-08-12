###
  Wadi sms tool web interface
###

angular.module('Wadi', ['ui.router'])
.config ($stateProvider, $urlRouterProvider) ->
  $stateProvider
  .state('home',
    url: '/'
    abstract: true
    templateUrl: 'index.html'
  )
  .state('home.login',
    url: '/login',
    templateUrl: 'templates/view_login.html'
  )

  $urlRouterProvider.otherwise('/login')

###
angular.module("Wadi", [])
.controller 'MainCtrl', ($scope, $log, $http) ->
  $scope.data = staticData

  $scope.formdata = {}
  $scope.submit = () ->
    nData = $("#dataForm").serializeObject()
    $log.info("Object mode: "+JSON.stringify(nData))
    $http.post "http://45.55.72.208/wadi/interface/post", nData
    .success (res) ->
      $log.info "Got result: "+JSON.stringify(res)
###
