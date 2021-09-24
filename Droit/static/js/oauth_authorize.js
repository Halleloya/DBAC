function getGeoCoordinatesAsync(){
    return new Promise((resolve, reject) => {
        var options = {
        enableHighAccuracy: true,
        timeout: 5000,
        maximumAge: 1
        };
        navigator.geolocation.getCurrentPosition(function(position) {
            if(position != null) {
                var crd = position.coords;
                resolve(crd.longitude  + ',' + crd.latitude)
            }
            resolve(null)
        }, function (err) {
        resolve(null)
        },
        options);
    });
}

async function getGeoCoordinatesSync() {
    let promise = await getGeoCoordinatesAsync();
    return promise;
}

function onConfirm() {
    let result = getGeoCoordinatesSync();
    var delimitter = ':';
    result.then(location => { 
        if(location != null){
            var inputList = document.getElementsByTagName("input");
            for(var i = 0;i < inputList.length; i++){
                if(inputList[i].value == 'polygon') {
                    inputList[i].value = inputList[i].value + delimitter + location;
                }
            }
            $("#authorizeForm").submit();
        }
    });
}

function onCancel() {
    window.location.href = "../dashboard/query";
}