/*
 * adds the ability to de-dupe an array
 */

var isSafari = navigator.vendor && navigator.vendor.indexOf('Apple') > -1 &&
               navigator.userAgent &&
               navigator.userAgent.indexOf('CriOS') == -1 &&
               navigator.userAgent.indexOf('FxiOS') == -1;

Array.prototype.unique = function() {
    var a = this.concat();
    for(var i=0; i<a.length; ++i) {
        for(var j=i+1; j<a.length; ++j) {
            if(a[i] === a[j])
                a.splice(j--, 1);
        }
    }
    return a;
};

/*
 * Bootstrap starts here by setting DMFsomething constants to the document by reading the HTML that is constructed by PHP of ALL academic programs
 * Javascript here does not talk to the server dynamically, but rather reads the URL and recinds / shows academic programs as needed.
 *
 * all codes used to determine settings are built by PHP in the dmf_page.tpl.php system
 * this is designed to aleviate load time by relying on drupal cache to push all programs to the page
 * at the same time and load a large HTML-laden document that contains all necessary data which JS can sort here
 * this avoids the complexity of working with real-time database calls through JSON/AJAX which is unnecessary because
 * the content is very static and brief -- after the readStateCheckInterval fires below,
 * all of this information is read and "shown" as css classes that default hide data are removed.
 */

const DMFPrograms = document.querySelectorAll(".dmf-program-list-item");
const DMFProgramsOptions = _DMF_ReturnArrayOfAllOptionCodes(DMFPrograms);
const DMFParents = document.querySelectorAll(".dmf-program-list-item.dmf-parent");
const DMFDropdowns = document.querySelectorAll(".dmf-dropdown");
const DMFDyanamicDisplayInfo = document.querySelectorAll(".dmf-dynamic-display-info");
var DMFCurrentCodes = [];


/*
 * every 10th of a second it checks for the ready state and changes information to visibile 
 * if the URL has parameters set to do so
 * 
 */
var readyStateCheckInterval = setInterval(function() {
    if (document.readyState === "complete") {
        clearInterval(readyStateCheckInterval);
        _DMF_CalculateDisplayOptions('--');
     }
}, 100);



/*
 * returns a parameter's value string if provided the parameter
 * else it returns all parameter values as an array
 */
function getAllUrlParameters(sParam) {
    var sPageURL = decodeURIComponent(window.location.search.substring(1)),
        sURLVariables = sPageURL.split('&'),
        sParameterName,
        parameterArray = [],
        i;

    for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');
        sParameterName[1] === undefined ? true : parameterArray.push(sParameterName[1]);        
          if (sParameterName[0] === sParam) {
            if(sParam !== null){
            return sParameterName[1] === undefined ? true : sParameterName[1];
            }
          }
    }
    return parameterArray;
};

/*
 *  Iterates through every parent and removes the stripe 
 *  when a selection is made - this provides "blink" feedback
 *  so if a users clicks something, and there isn't a data-resort, they feel they
 *  have succeeded, but they need to click something else... avoids the need of a 
 *  "options change nothing, try again" message
 */

function _remove_stripe_from_parents(elements){
  Object.keys(elements).forEach(function (k){
      elements[k].classList.remove('stripe');
  });
}

/*
 *  Parent-sriping is difficult, it needs staggered from the document by about 1/2 second
 *  this is because when the options refresh the page they modify the classes in the dom
 *  these classes  are the easiest fastest way to see what is hiden or not... only visible
 *  items need a stripe - and only parents - it's not a simple as even/odd 
 */
function _add_stripe_to_open_parents(elements){
  var isOdd = function(x) { return x & 1; };
  var isEven = function(x) { return x % 2 == 0;}
  let stripeArray = [];
   Object.keys(elements).forEach(function (k){
    if(elements[k].classList.contains('dmf-program-hide') == false){
      stripeArray.push(elements[k]);
    }
  });
  let count = 1;
    Object.keys(stripeArray).forEach(function(k){
    if(isEven(count)){
      stripeArray[k].classList.add('stripe');
    }
    count++
  });
}

/*
 *  dataCode is a string
 *  returns nothing
 *  the primmary active function that is triggered after page load from the default selection
 *  as well as if the click events are detected on dropdown items.
 *  receives a dataCode which represents what was selected or what is default in the URL
 */
function _DMF_CalculateDisplayOptions(dataCode){
  console.log('datacode: ' +  dataCode);
  _remove_stripe_from_parents(DMFParents);
  let selectedCodes = _DMF_ReturnSelectedCodesInArray(dataCode);
  _DMF_toggle_dynamic_DMF_department_advertisement(selectedCodes);
  let programsResultArray = _DMF_ToggleIfDataCodeMatches(DMFPrograms,dataCode,selectedCodes);
  // _DMF_HideEmptyChildGroups()
  DMFCurrentCodes = DMFCurrentCodes.concat(programsResultArray).unique();
  _DMF_DisableInvalidOptions(DMFCurrentCodes);
  // wait half a second before highlighting parents
  setTimeout(function() {_add_stripe_to_open_parents(DMFParents);}, 500);
}

/*
 *  Change event listener waits for modifications to the dropdown boxes at the top.
 *  When they occur this listener will pass the target value to the function responsible 
 *  for resetting the page information
 */
document.addEventListener('change', function (event) {
  // this event was an actual mouse-click on the dmf-dropdown...process it.
  if (event.target.matches('.dmf-dropdown')){
    // first run the process which shows programs
    _DMF_CalculateDisplayOptions(event.target.value);
    // next set the dropdown box options to what they should be 
    _DMF_SetDefaultSelectedOptions(event.target,event.target.value);
    // this is designed to look for clicks in icons and tags that are clickable and will
    // quick-sort the list without messing with the drop-down (good for cell phones)
  }
}, false);



/*
 *  Click listener identifies any event occuring that matches certain classes
 *  this is the primary function by which the user interacts with the list
 */
document.addEventListener('click', function (event) {
  // if the event target mathes these classes, a clickEvent is generated matching the ID that is set
  // in the dataset.code of the clicked object
  // javascript will then repeat a click-event action again - firing this function again,
  // but the second time it's fired, the click matches the dropdown
  // was unsure of how else to perform this function - may need a rework ... seems kinda hacky

  if (event.target.matches('.dmf_format-icon') ||
      event.target.matches('.dmf-format-bg-icon') ||
      event.target.matches('.dmf_type-tag > span') ||
      event.target.matches('.dmf_program_type-tag > span') ||
      event.target.matches('.dmf_degree_type-tag > span')){
   
    // gets the code option contained in the specific click element
    let codeArray = event.target.dataset.code.split("-");
    // uses the code element to get the proper option in the list
    let changedElement = document.getElementById(codeArray[1]);


    if(isSafari){
      console.log('isSafari = ' + isSafari);
      // this stuff only works on safari
      let changedElementParent = changedElement.parentElement;
      changedElementParent.value = changedElement.value;
      changedElementParent.dispatchEvent(new Event("change", { bubbles: true }));
    } else {
      console.log('NOT SAFARI');
      // sets that option to selected -- which work for chome & everything but safari
      changedElement.defaultSelected = true;
      changedElement.selected = true;
    }

    // semds it to the function which refreshes the screen
    _DMF_CalculateDisplayOptions(changedElement);
  }

  // maybe the clicked the "reset-all" button
  if(event.target.matches('#dmf-fixed-button')){
    Object.keys(DMFDropdowns).forEach(function (key) {
      // leaving the second parameter blank will force the function to default to "all"
      _DMF_SetDefaultSelectedOptions(DMFDropdowns[key]);
    });
    // tell the calculate function to display everything esentially
    _DMF_CalculateDisplayOptions('--');
    return;
  }

}, false);

/*
 *  Since the page doesn't actually reset, the default selected options on page load need removed with each click on the options
 *  Cycle through the clicked target and get rid of all options that were default selected.
 */
function _DMF_SetDefaultSelectedOptions(target,value = false){
  // if the value is false, we're going to remove all default selected
  if(!value){
    Object.keys(target).forEach(function (key) {
        target[key].selectedIndex = 0;
        target[key].selected = false;
        target[key].defaultSelected = false;
        // all options are going to be reset, except for the "all" option
        if(target[key].value == "--"){
          target[key].selectedIndex = 1;
          target[key].selected = true;
          target[key].defaultSelected = true;
        }
    });
  // else the value is actually a string that represents the target
  } else {
    Object.keys(target).forEach(function (key) {
        target[key].selectedIndex = 0;
        target[key].selected = false;
        target[key].defaultSelected = false;
        // we have a value which needs now to be the default and selected etc.
        if(target[key].value == value){
          target[key].selectedIndex = 1;
          target[key].selected = true;
          target[key].defaultSelected = true;
        }
    });
  }
}


/*
 *  This toggle functionality written to replace Collapse in bootstrap-native-4v.js
 *  dmf_ezcollapse.js is the replacement that ships with dmf module.  Collapse was leading to 
 *  many page reflow issues because of it's intense overhead.  It is designed to work in all situations
 *  with a target separate from the collapsable button.  Also there were strange overrides necessary
 *  with collapse to prevent the click of the same item and thereby collapse itself.
 *  if Parent is true, this system will not test to see if it needs to disable the parent
 */
function _DMF_ToggleIfDataCodeMatches(elements,dataCode = '',array){
  //console.log(elements);
  collectedCodes = [];
  let childElements = [];
  let parentElements = [];
  let processElements = [];
  //first, parents and children need to process separately with children going first.
  for(let i = 0; i < elements.length; i++){
    if(elements[i].classList.contains('dmf-parent')){
      parentElements[i] = elements[i];
      // console.log(elements[i]);
    } else if (elements[i].classList.contains('dmf-child')) {
      // console.log(elements[i]);
      childElements[i] = elements[i];
    }
  }

  processElements = processElements.concat(childElements,parentElements);

  Object.keys(processElements).forEach(function (k) {
    let e = processElements[k];
    let bottomRowDiv = false;
    let excludeChildren = false;
    let parentsChildrenArray = [];
    let childCodeArray = [];
    // complex necessity of having a child class declared which will be added up
    // to include into the parent class's height for shrink and grow purposes.
    let childClassDetected = '';
    // first detect the second SubNodes of each Parent, this is div.class "dmf-prog-list-bottom-row"
    if(e.querySelector('.dmf-prog-list-bottom-row')){
      bottomRowDiv = e.querySelector('.dmf-prog-list-bottom-row');
    }

    // childNodes of selected element may not be actual children nodes
    if(bottomRowDiv.childNodes !== undefined){
      Object.keys(bottomRowDiv).forEach(function(childKey) {
        if(bottomRowDiv[childKey].classList !== undefined){
          if(bottomRowDiv[childKey].classList.contains('dmf-child-program')){
            parentsChildrenArray.push(bottomRowDiv[childKey]);
          }
        }
      });
    }
    
    // cycle the array for code arguments from the URL or selection boxes
    if(array.length <= 0){
      // there are NOT codes currenlty selected, so "ALL" must be selected - cycle and turn on everything
      e.EZCollapse.growMe();
      // if any SubNodes exist (concentration containers) these cointainers also need to growME();
      if(parentsChildrenArray.length > 0){
        Object.keys(parentsChildrenArray).forEach(function(childKey) {
          parentsChildrenArray[childKey].EZCollapse.growMe();
        });
      }
    } else {
      // there is a code selected from the dropdowns, we need to process this code
      // run through each and every item in elements
      // this is itended to run once with children, and then again with parents exclusively
      let codeArray = e.dataset.codes.split("|");
      // collect codes that are still viable within each remaining selection
      // these codes will be used to determine what is still available to select by
      // the dropdown boxes
      if(arrayContainsArray(array,codeArray)){
        // collect the codes together this will be returned
        collectedCodes = collectedCodes.concat(codeArray);

        // only run this if the item is a parent
        if(parentsChildrenArray.length > 0){
          Object.keys(parentsChildrenArray).forEach(function(childKey) {
            let childCodeArray = [];
            childCodeArray = parentsChildrenArray[childKey].dataset.codes.split("|");
            if(arrayContainsArray(array,childCodeArray)){
              childClassDetected = 'dmf-child';
            }
          });
          // there were children, but none matched the codes provided... so exclude from height
          if(childClassDetected == ""){excludeChildren = true; e.EZCollapse.reduceMe(0,500);}
        }
      // grow the element because there is a match
        e.EZCollapse.growMe(0,500,childClassDetected,excludeChildren);
      } else {
        e.EZCollapse.shrinkMe(0,500,excludeChildren);
      }
    }
  });
  return collectedCodes;
}


/*
 * loops through each dropdown and returns an array of selected values (codes)
 */
function _DMF_ReturnSelectedCodesInArray(dataCode = ''){
  let outputArray = [];
  Object.keys(DMFDropdowns).forEach(function (k) {
    // let i = DMFDropdowns[k].selectedIndex;

    if(DMFDropdowns[k].value !== '--'){
      outputArray.push(DMFDropdowns[k].value);
    }
  });
  return outputArray;
}


/*
 * Returns TRUE if the first specified array contains all elements
 * from the second one. FALSE otherwise.
 */
function arrayContainsArray(subset, superset){
  //console.log(typeof subset);
  //console.log(typeof superset);
  if (0 === subset.length){
    return false;
  }

  return subset.every(function (value){
    return (superset.indexOf(value) >= 0);
  });
}

/*
 * Returns TRUE if the first specified array contains ANY elements
 * from the second one. FALSE otherwise.
 */
function objectIntersectsWithObject(subsetObj, supersetObj){
  let subset = Object.values(subsetObj);
  let superset = Object.values(supersetObj);
  
  console.log(subset);
  console.log(superset);

  if (0 === subset.length){
    return false;
  }

  let intersection = superset.filter(element => subset.includes(element));

  if(intersection.length > 0){
    return true;
  } else {
    return false;
  }
}



/* 
 *  Receives an array of codes that represents all the currently shown programs
 *  cycles through all the options on the page and disables them if the value 
 *  does not match the current reduce-able options.
 */ 
 function _DMF_DisableInvalidOptions(DataCodeArray){
  // loop through each program and collect all the available options see it has 
  let selectedCodeArray = [];
  let thisOptionCodeArray = [];
  // first, which field are selected already? - Collect them together, if any
  Object.keys(DMFDropdowns).forEach(function (field) {
    if(DMFDropdowns[field].value !== '--'){
      selectedCodeArray.push(DMFDropdowns[field].value);
    }
  });

  // next cycle through each and every option; 
  // disable any options that will result in zero programs
  Object.keys(DMFDropdowns).forEach(function (field) {
    Object.keys(DMFDropdowns[field]).forEach(function (option) {
      // start off each loop of options prepared with the options that were already selected
      thisOptionCodeArray.length = 0;
      thisOptionCodeArray = thisOptionCodeArray.concat(selectedCodeArray);

      if(DMFDropdowns[field][option].value !== '--'){
        // now, add the value of the current option we're inspecting to see if it will result in dead-end lookup 
        thisOptionCodeArray.push(DMFDropdowns[field][option].value);

        // finally, we need to check every program individually to see if that program
        // has the same options in thisOptionCodeArray
        if(_DMF_DetectIfOptionsAreADeadEnd(thisOptionCodeArray)){
          DMFDropdowns[field][option].classList.add('dmf-hide');
          DMFDropdowns[field][option].disabled = true;
        } else {
          DMFDropdowns[field][option].classList.remove('dmf-hide');
          DMFDropdowns[field][option].disabled = false;
        }
      }
    });
  });
 }

/*
 *  receives an array - returns a boleen
 *  helps discover if an option in the dropdowns needs disabled as a dead end.
 *  Loops through all the Programs and and checks if the options array provided
 *  match the dataset.codes within the DMFPrograms array
 *  if nothing matches whatsoever it returns a false, else it returns true as soon as it makes a match since 
 *  there is at least 1 program that keeps the options from being a "Dead end selection"  
 */
function _DMF_DetectIfOptionsAreADeadEnd(options){
  for(let i = 0; i < DMFPrograms.length; i++ ){
    if(arrayContainsArray(options, DMFPrograms[i].dataset.codes.split("|"))){
      // found a match, this option is still good
      return false;
    }
    // uh oh, no matches, go to the next program
  }
  // for loop has finalized, there must be no matches for this option...deadend is detected 
  return true;
}


/*
 *  Loops through all the Programs and grabs every Data-code then de-dupes it
 *  these are ALL the possible options available
 *  returns an array() of all available options
 */
function _DMF_ReturnArrayOfAllOptionCodes(programs){
  let array = [];
  programs.forEach(function(e){
    // for each program, split the string separated by "|" into an array and collect it
    array = array.concat(e.dataset.codes.split("|"));
  });
  return array.unique().sort();
}

// These should eventually be gobal functions instantiated at the module layer
window.mobileCheck = function() {
  let check = false;
  (function(a){if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino/i.test(a)||/1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(a.substr(0,4))) check = true;})(navigator.userAgent||navigator.vendor||window.opera);
  return check;
};

window.mobileCheckValue = window.mobileCheck();

// These should eventually be gobal functions instantiated at the module layer
window.dmf_block_IOS_detect_send = function(event, href = '') {
  var userAgent = window.navigator.userAgent;
  var ele = document.activeElement;
  let isIOS = !!(/iPad|iPhone|iPod/.test(navigator.platform) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1)) && !window.MSStream;

  if (isIOS && event !== 'click') {
    // click simply sucks somehow on IOS - they have such janky inconsistant crap under the hood of safari
    window.location.href = ele.value;
  } else if (window.mobileCheckValue && event === 'change') {
    // changes will occure on the website each time someone up/down arrows, so we want to NOT send someone to the result
    // as soon as this 'false' change occures.  We need users to be able to up/down arrow through the list and then hit space or enter to go forward
    // so we need to check for all phones etc - not sure why touchstart isn't working all the time - but it doesn't.
    window.location.href = ele.value;
  } else if ((event === 'mousedown' || event === 'touchstart') && (href !== undefined)){
    // Can't use 'click' or 'change' event because I'm trying to isolate screen readers on mousedown or touchstart with dmf_block_checkTabPress()
    // click simply sucks somehow on IOS - they have such janky crap 
    window.location.href = href;
  } else {
    // essentially we want NOTHING to happen which allows the listener:  document.addEventListener('keyup', function (e) {
    // to process the keypresses and send the user where they wish to go.
    // console.log('Event:' + event + '; IOS:' + isIOS);
  }
};

/*
 *  adds and eventListener to check for TAB, ARROW, ENTER & SPACE key presses within the DMF block 
 */
document.addEventListener('keyup', function (e) {
    var ele = document.activeElement;
      switch (event.keyCode) {
        case 37:
        case 38:
        case 39:
        case 40:
          // console.log('arrow keys pressed');
        break;
        case 32:
        case 13:
        if(typeof lastname !== ele.value){
          if(ele.value.includes('/')){
            window.location.href=ele.value;
          }          
        }
        break;
      }
}, false);



function _DMF_toggle_dynamic_DMF_department_advertisement(selectedCodes){
  // get all elements that contain the class: ".dynamic-dmf-department-advertisement"
  // don't use this on the other pages that have dynamic-dmf-sidebars ... only the dmf page-programs
  elements = document.querySelectorAll("body.html.page-programs .dynamic-dmf-sidebar");

  // cycle through all the elements and look for one of the selected codes if it exists
  for(let i = 0; i < elements.length; i++){ let classList = 
  elements[i].classList;
    // console.log(objectIntersectsWithObject(selectedCodes,classList));
    // does one of the selectedCodes (dropdown list) exist in the classList of this element?
    if(objectIntersectsWithObject(selectedCodes,classList)){
      // console.log('YEP, it contains one of:' + selectedCodes);
      if(classList.contains('d-none')){
        classList.remove('d-none');
      }
    } else {
      // console.log('NOPE, IT ONLY HAS:' + classList);
      classList.add('d-none');
    }
  }
}