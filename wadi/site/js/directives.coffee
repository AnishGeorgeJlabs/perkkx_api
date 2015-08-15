###
  Works like a charm :D
  Tested on Sat, 15 Aug, 06:44 PM
###
angular.module('Wadi.directives', [])
.directive 'wdRangeInput', () ->
  restrict: 'E'
  scope:
    label: '=label'
    model: '=model'
  templateUrl: './templates/dir_range.html'
  controller: ($scope, $log) ->
    $scope.lt = "Less than"
    $scope.eq = "Equal to"
    $scope.gt = "More than"
    $scope.bw = "Between"

    $scope.data =
      op: ''
      min: 1
      max: 2

    compileResult = () ->
      $scope.model = switch $scope.data.op
        when '' then ''
        when $scope.bw then "#{$scope.bw} #{$scope.data.min} and #{$scope.data.max}"
        when $scope.eq then "#{$scope.data.min}"
        else "#{$scope.data.op} #{$scope.data.min}"

    $scope.$watchCollection(
      'data',
      (nVal, oVal) ->
        if nVal.min != oVal.min and nVal.min != null and nVal.min >= nVal.max
          $scope.data.max = $scope.data.min + 1
        if nVal.max != oVal.max and nVal.max != null and nVal.max <= nVal.min
          $scope.data.min = $scope.data.max - 1
        compileResult()
    )

    # The genius touch, add this handler to the ng-blur of both inputs
    $scope.recover = () ->
      if $scope.data.min == null or $scope.data.min <= 0
        $scope.data.min = 1
      if $scope.data.max == null
        $scope.data.max = $scope.data.min + 1
