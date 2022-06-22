(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    // AMD support:
    define([], factory);
  } else if (typeof module === 'object' && module.exports) {
    // CommonJS-like:
    module.exports = factory();
  } else {
    // Browser globals (root is window)
    var DMFEZ = factory();
    root.EZCollapse = DMFEZ.EZCollapse;
    root.EZFixedButton = DMFEZ.EZFixedButton;
  }
}(this, function () {
  "use strict";
  
  var globalObject = typeof global !== 'undefined' ? global : this||window,
    HTML = document.documentElement,
    dataToggle     = 'data-toggle',
    dataTarget     = 'data-target',
    isAnimating    = 'isAnimating',
    self           = this,
    counter = 0,
    collapse       = null;

  var queryElement = function (selector, parent) {
    var lookUp = parent ? parent : document;
    return typeof selector === 'object' ? selector : lookUp.querySelector(selector);
  }

    // event attach jQuery style / trigger  since 1.2.0
  var on = function (element, event, handler) {
    element.addEventListener(event, handler, false);
  }
  
  var DMFEZ = globalObject.DMFEZ = {};
  var supports = DMFEZ.supports = [];
  DMFEZ.version = '2.0.25';  //IDK what this is for
  
  var limit = 100;
  var speed = 5;
  // cool easing functions from https://gist.github.com/gre/1650294
  const easeOut = p => (--p)*p*p+1; 
    // accelerating from zero velocity 
  const easeInQuad = p => p*p;
    // decelerating to zero velocity
  const easeOutQuad = p => p*(2-p);
    // acceleration until halfway, then deceleration
  const easeInOutQuad = p => (p<.5) ? 2*p*p : -1+(4-2*p)*p;
    // accelerating from zero velocity 
  const easeInCubic = p => p*p*p;
    // decelerating po zero velocity 
  const easeOutCubic = p => (--p)*p*p+1;
    // acceleration until halfway, phen deceleration 
  const easeInOutCubic = p => (p<.5) ? 4*p*p*p : (p-1)*(2*p-2)*(2*p-2)+1;
    // accelerating from zero velocity 
  const easeInQuart = p => p*p*p*p;
    // decelerating to zero velocity 
  const easeOutQuart = p => 1-(--p)*p*p*p;
    // acceleration until halfway, phen deceleration
  const easeInOutQuart = p => (p<.5) ? 8*p*p*p*p : 1-8*(--p)*p*p*p;
    // accelerating from zero velocity
  const easeInQuint = p => p*p*p*p*p;
    // decelerating to zero velocity
  const easeOutQuint = p => 1+(--p)*p*p*p*p;
    // acceleration until halfway, then deceleration 
  const easeInOutQuint = p => (p<.5) ? 16*p*p*p*p*p : 1+16*(--p)*p*p*p*p;

  
  // EZFixedButton Deffinition
  // ===================
  var EZFixedButton = function( element, options ) {
    var self = this;
    let report = '';
    element = queryElement(element);
    options = options || {};

    this.calculate = function(){
      keep_element_within_parent(element);
      toggle_visibility_of_element_by_parent_height(element);
      move_element_to_parent_right(element);
    }
    // designed to position the element on the x axis when the screen
    // resizes to retain sizing in responsive layouts
    // doesn't look so good "jumping" - but it's ok
    function move_element_to_parent_right(element){
      let parentCords = element.parentNode.getBoundingClientRect();
      let rightSide = parentCords.width + "px";
      element.style.width = rightSide;
    }

    // conrolls y-position of the element by calculating if the parent is above or below the center of the screen
    // should not allow the the element to position itself outside of the parent's limits...but retain "fixed" position
    // which is easy on processing and looks ultra-smooth.
    function keep_element_within_parent(element){
      let parentCords = element.parentNode.getBoundingClientRect();
      let elementCords = element.getBoundingClientRect();
      let scrollTop = document.documentElement.scrollTop;
      let scrollMiddleScreen = (screen.height / 2) + scrollTop
      // the parent's top edge is below crossed the middle of the screen
      if(parentCords.y > screen.height / 2){
        // put the element below the center of the screen by the amount that the parent is below it (requires a Math.abs(positive))
        element.style.top = screen.height / 2 + Math.abs(parseInt(((screen.height  / 2) - parentCords.y))) + "px";
      // the parent's bottom edge (plus element height) is above the middle of the screen
      } else if (!(parentCords.y + parentCords.height  > (screen.height / 2) + elementCords.height)){
        // put the element above the bottom of the parent, even if that means a negative height;
        element.style.top = parseInt(parentCords.y + parentCords.height - elementCords.height) + "px";
      } else {
              // put the element directly in the center of the screen
        element.style.top = screen.height / 2 + "px";
      }
    }

    // if the parent is not big enough, simply hide or show the element if the parent size changes.
    function toggle_visibility_of_element_by_parent_height(element){
      let parentCords = element.parentNode.getBoundingClientRect();
      let elementCords = element.getBoundingClientRect();
      if(parentCords.height < elementCords.height){
        element.classList.add('dmf-invisible');
      } else {
        element.classList.remove('dmf-invisible');
      }
    }

    /* not currently used -- forces the parent to have a height at least as equal to child */
    function increase_parent_height_if_less_than_element(element){
      let parentCords = element.parentNode.getBoundingClientRect();
      let elementCords = element.getBoundingClientRect();
      if(parentCords.height < elementCords.height){
        element.parentNode.style.minHeight = elementCords.height;
      }
    }

    document.addEventListener('click', function (event) {
      increase_parent_height_if_less_than_element(element);
      self.calculate();
    });


    window.addEventListener('resize', function (event) {
      increase_parent_height_if_less_than_element(element);
      self.calculate();
    });

    document.addEventListener('scroll', function (event) {
      increase_parent_height_if_less_than_element(element);
      self.calculate();
    });

    // element depends on DOM being fully calculated.
    // Wait 2 Sec after DOM load to calculate position and remove dmf-invisibility of element
    document.addEventListener('DOMContentLoaded', (event) => {
      setTimeout(function(){
        self.calculate();
      }, 2000);
    })


     // init
    element['EZFixedButton'] = this;
  };
  // ResetButton DATA API
  // =================
  supports['push']( ['EZFixedButton', EZFixedButton, '['+dataToggle+'="DMF-Fixed-Button"]' ] );

  // EZCollapse Deffinition
  // ===================
  var EZCollapse = function( element, options ) {
    // console.dir(element);
    element = queryElement(element);
    options = options || {};

    this.limit = limit;

    let growMeRunning = false;
    let shrinkMeRunning = false;
    let reduceMeRunning = false;
    let distance = element.scrollHeight; // pixels
    let progress = 0;
    let totalChildHeight = 0;

    /*
     *  returns the absolute which includes margins etc.
     */
    function getAbsoluteHeight(el) {
      // Get the DOM Node if you pass in a string
      el = (typeof el === 'string') ? document.querySelector(el) : el; 

      var styles = window.getComputedStyle(el);
      var margin = parseFloat(styles['marginTop']) +
                   parseFloat(styles['marginBottom']);

      return Math.ceil(el.offsetHeight + margin);
    }

    /*
     *  HELPER FUNCTION FOR DMF Concentrations 
     *  This private function helps find grand childen by the classname provided and returns  
     *  the collective scroll height of all children than match the class requested
     *  "el" is the current element that is being searched for grandKids
     *  function needs to detect if these items have a height of 0 or not... if so.. add new height to parent, if not - don't add - it will double what is there already 
     */
     function includeHeightof_DMF_GrandKidsByClass(el,grandKidClass){
      let children = [];
      let childArray = Array.from(el.childNodes);
      childArray.forEach(function(child){
        if(child.classList !== undefined){
          if(child.classList.contains('dmf-child-program')){
            children.push(child); 
          }
        } 
      });
      let height = 0;
      let topRowHeight = 0;
      children.forEach(function(e){
        console.dir(e);
        console.dir(e.children);
        let lastIndex = e.children.length - 1;
        // Only element typ;es are considered
        if(e.nodeType === 1){
          if(e.classList.contains('dmf-prog-list-top-row')){
            topRowHeight = getAbsoluteHeight(e)
            e.children[0].classList.remove("dmf-program-hide");
            e.children[lastIndex].classList.remove("dmf-program-hide");
            e.children[0].removeAttribute('aria-hidden');
            e.children[lastIndex].removeAttribute('aria-hidden');
           } else if (e.nodeType === 1 && e.classList.contains('dmf-prog-list-bottom-row')){
            e.children[0].classList.remove("dmf-program-hide");
            e.children[lastIndex].classList.remove("dmf-program-hide");
            e.children[0].removeAttribute('aria-hidden');
            e.children[lastIndex].removeAttribute('aria-hidden');
          }
        }
        let grandKids = e.childNodes;
        grandKids.forEach(function(grandKid){
        // Only elements that have a zero height will be considered 
          //if(grandKid.nodeType === 1 && parseInt(grandKid.style.height) > 0){
          if(grandKid.nodeType === 1){
            if(grandKid.classList.contains(grandKidClass)){
              height = height + grandKid.scrollHeight;
            }
          }
        });
      });
      return height + topRowHeight;
    }

    /*
     *  HELPER FUNCTION FOR DMF Concentrations 
     *  this excludes any secondary unwanted classes from the distance to shrink
     */
     function excludeHeightof_DMF_GrandKids(el){
      let children = el.childNodes;
      let topRowHeight = 0;
      children.forEach(function(e){
        let lastIndex = e.children.length - 1;
        // Only element types are considered
        if(e.nodeType === 1 && e.classList.contains('dmf-prog-list-top-row')){
          topRowHeight = getAbsoluteHeight(e);
        } else if (e.nodeType === 1 && e.classList.contains('dmf-prog-list-bottom-row')){
          e.children[0].classList.add("dmf-program-hide");
          e.children[lastIndex].classList.add("dmf-program-hide");
          e.children[0].setAttribute('aria-hidden', true);
          e.children[lastIndex].setAttribute('aria-hidden', true);
        }
      });
      return topRowHeight;
    }

    this.growMe = function(delay = 0, duration = 500, childHeightClass = '', excludeChildren = false){
      element.classList.remove('dmf-program-hide');
      element.removeAttribute('aria-hidden');
      element.classList.remove('dmf-height-auto');

      if(element.classList.contains('dmf-parent')){
        element.children[0].children[1].tabIndex = 0;
      } else if(element.classList.contains('dmf-child-program')) {
        element.children[0].tabIndex = 0;
      } else if (!element.classList.contains('dmf-child')){
        if(element.children[0].classList.contains('dmf-child-title')){
            element.children[0].tabIndex = 0;
        }
      }

      // it is possible that elements have children elements that are difficult to measure otherwise
      if(excludeChildren){distance = excludeHeightof_DMF_GrandKids(element);}
      // there have been children detected, and to confirm it, there is no excludeChildren code... ensure children & other classes are shown
      if(!excludeChildren && childHeightClass !== '') {distance = includeHeightof_DMF_GrandKidsByClass(element,childHeightClass);} else {
        // is growMe Runing?  Is it already grown?
        if(element.offsetHeight == distance || growMeRunning){return} else {growMeRunning = true;}        
      }

      let start = null;
      let heightValue = 0;
      progress = 0;

      function growHeight(timestamp){
        if (!start) start = timestamp;
        let stopwatch = timestamp - start;
        progress = Math.min(stopwatch / duration, 1);
        heightValue = (distance * easeInOutQuad(progress)).toFixed(2) + 'px'
        element.style.height = heightValue;
        if(progress < 1){ // still have time left to proccess this
          requestAnimationFrame(function(timestamp){
             growHeight(timestamp);
          });          
        } else {
          growMeRunning = false;
          element.style.height = "auto";
        }
      }
      if(delay !== 0){
        setTimeout(function() {requestAnimationFrame(growHeight);}, delay);
      } else {
        requestAnimationFrame(growHeight);
      }
    };


    this.reduceMe = function(delay = 0, duration = 500){
      let start = null;
      progress = 0;
      distance = excludeHeightof_DMF_GrandKids(element);
      if(element.offsetHeight == distance || reduceMeRunning){return} else {reduceMeRunning = true;}
      function reduceHeight(timestamp){
        if (!start) start = timestamp;
        let stopwatch = timestamp - start;
        progress = Math.min(stopwatch / duration, 1);
        // it is possible that elements have children elements that are difficult to measure otherwise
        element.style.height = (distance - (distance * easeInOutQuad(progress))).toFixed(2) + 'px';
        if(progress < 1){ // still have time left to proccess this
         requestAnimationFrame(function(timestamp){
            reduceHeight(timestamp);
         });          
        } else {
          reduceMeRunning = false;
        }
      }
      if(delay !== 0){
        setTimeout(function() {requestAnimationFrame(reduceHeight);}, delay);
      } else {
        requestAnimationFrame(reduceHeight);
      }
    }


      this.shrinkMe = function(delay = 0, duration = 500, excludeChildren = false){
      // is shrinkMe Runing?  Is it already shrunk?
      if(element.offsetHeight == 0 || shrinkMeRunning){return} else {shrinkMeRunning = true;}
      // if excludeChildren fires, we need to calculate and exclude anyting unwanted 
      if(excludeChildren){distance = excludeHeightof_DMF_GrandKids(element);}
      let start = null;
      progress = 0;
      function shrinkHeight(timestamp){
        if (!start) start = timestamp;
        let stopwatch = timestamp - start;
        progress = Math.min(stopwatch / duration, 1);
        // it is possible that elements have children elements that are difficult to measure otherwise
        element.style.height = (distance - (distance * easeInOutQuad(progress))).toFixed(2) + 'px';
        if(progress < 1){ // still have time left to proccess this
         requestAnimationFrame(function(timestamp){
            shrinkHeight(timestamp);
         });          
        } else {
          shrinkMeRunning = false;
          element.classList.add('dmf-program-hide');
          element.setAttribute('aria-hidden', true);
          if(element.classList.contains('dmf-parent')){
            element.children[0].children[1].tabIndex = -1;
          }

          if(element.children[0].classList.contains('dmf-child-title')){
              element.children[0].tabIndex = -1;
          }
        }
      }
      if(delay !== 0){
        setTimeout(function() {requestAnimationFrame(shrinkHeight);}, delay);
      } else {
        requestAnimationFrame(shrinkHeight);
      }
    };
    
    // init
    if ( !('EZCollapse' in element ) ) { // prevent adding event handlers twice
      on(element, 'click', this.toggle);
    }
    element['EZCollapse'] = this;
  };
  
  // DMF-COLLAPSE DATA API
  // =================
  supports['push']( ['EZCollapse', EZCollapse, '['+dataToggle+'="DMF-EZ-collapse"]' ] );
  
  /* Native Javascript for Bootstrap 4 | Initialize Data API
  --------------------------------------------------------*/
  var initializeDataAPI = function( constructor, collection ){
      for (var i=0, l=collection['length']; i<l; i++) {
        new constructor(collection[i]);
      }
    }, initCallback = DMFEZ.initCallback = function(lookUp){
      lookUp = lookUp || document;
      for (let i=0, l=supports['length']; i<l; i++) {
        initializeDataAPI( supports[i][1], lookUp['querySelectorAll'] (supports[i][2]) );
      }
    };
  
  // bulk initialize all components
  document['body'] ? initCallback() : on( document, 'DOMContentLoaded', function(){ initCallback(); } );
  
  return {
    EZCollapse: EZCollapse,
    EZFixedButton: EZFixedButton
  };
}));