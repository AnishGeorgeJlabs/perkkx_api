###
  Wadi sms tool web interface
###

angular.module('Wadi', ['ui.router', 'angularjs-dropdown-multiselect', 'Wadi.form'])
.config ($stateProvider, $urlRouterProvider) ->
  $stateProvider
  .state('login',
    templateUrl: './templates/view_login.html'
    controller: 'LoginCtrl'
  )
  .state('form',
    templateUrl: './templates/view_main.html'
    controller: 'FormCtrl'
  )
  .state('test',
    templateUrl: './templates/view_test.html'
    controller: 'TestCtrl'
  )

.controller 'MainCtrl', ($scope, $state, $http, $log) ->
  $log.debug "Main executed"
  $state.go('form')     # TODO, change

  isLoggedIn = false

  $scope.checkLogin = () -> isLoggedIn

  $scope.login = (username, pass) ->
    $log.debug "Got submission #{username}, #{pass}"
    $http.post "http://45.55.72.208/wadi/interface/login", {
      username: username,
      password: pass
    }
    .success (result) ->
      $log.debug "Got result: #{JSON.stringify(result)}"
      isLoggedIn = result.success
      if isLoggedIn
        $state.go('form')
      else
        alert "Authentication failed"


.controller 'LoginCtrl', ($scope, $log) ->
  $scope.data = {
    username: ''
    password: ''
  }

  $scope.submit = () ->
    $log.debug "Submitting : #{JSON.stringify($scope.data)}"
    $scope.$parent.login($scope.data.username, md5($scope.data.password))
    $scope.data.username = ''
    $scope.data.password = ''

.controller 'TestCtrl', ($scope, $state, $log) ->
  $scope.selected = []
  $scope.sampleData = [
    'electronics', 'shoes', 'sports bags', 'goodies'
  ]



  ###
  $scope.sampleData = [
    {id: 1, label: 'electronics'},
    {id: 2, label: 'shoes'},
    {id: 3, label: 'sports'}
  ]

  ###
