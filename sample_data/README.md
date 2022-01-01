## GeoAttributes Based Authorization

Simply put, this feature authorizes a user based on his/her location. Refer to the following file LocationBasedAuthorization/example_policy_location.json for
an example policy.

1) This policy contains a new rule 'GeoInside'. The parameter of this rule is a list of coordinates which represents a polygon.
2) To visualise this polygon
	-  Navigate to http://geojson.io/
	-  Copy the contents of the file 'LocationBasedAuthorization/PolygonCoordinates.txt' and paste it in the JSON text box
	-  You should be able to see a polygon which approximately covers a part of Columbia University.
	-  Modify the coordinates and choose a polygon which represents your current location from the map.
3) Copy the coordinates of the polygon that you have chosen in the last step and paste the array of coordinates to 'LocationBasedAuthorization/example_policy_location.json' file.
	- In the file, Find the 'GeoInside' condition and paste the coordinates in the values field of this condition.
	- Double check all opening and closing square and flower braces as it is easy to miss one while copy pasting.
4) Positive Test case : To test the feature individually, perform the following steps:
	- Delete all the previous policies if any
	- Register the LocationBasedAuthorization/example_policy_location.json file
	- The policy states that if the user location is present inside the polygon that is represented by the policy, allow access or else deny
	- Search for things in the directory. Register if there is not a single thing registered.
	- You first have to click on Authorize button. It will redirect to a new page. Cick on confirm and allow the directory to access your location.
	- Now click on Request button, You should be able to see the details of the thing.
5) Negative Test cases :
	- If you had clicked on Request button without clicking on authorize button then your request to access the thing will be denied.
	- You may register a policy with a different polygon that does not enclose your location by following the steps from point2 to point3,
		Since your location now falls outside the polygon, Your access request should again be denied.

### Common Issues

1) I am unable to register the policy after changing the coordinates in the policy file.

Answer : Make sure after copying the coordinates, your policy file is still in valid JSON format.
Also note that the values parameter is a list of coordinates where each element in turn is a list of two elements
containing latitude and longitude. Make sure that you adher to the format.

2) I am able to access the thing without authorizing first.

Answer : Your browser may have cached the location that you have previously authorized.  Delete the cache of your browser
to test the feature from scratch or let it be as it is by design. If you have not previously authorized though then this
should not be the case.

## Dynamic Attributes

This Feature authorizes a user based on his number of successful access request for a particular IoT Device. Refer to the following file
AccessFrequencyBasedAuthorization/access_frequency_policy.json for an example policy.
1) This policy contains a new rule 'AccessFrequencyLte'. The parameter of this rule is a list containing two elements.
The first element represents the number of times a resource can be accessed. The second time represents the reset time.
2) Test case : To test the feature individually, perform the following steps:
	- Delete all the previous policies if any
	- Register the AccessFrequencyBasedAuthorization/access_frequency_policy.json file
	- The policy states that you can access a particular resource for 5 times within 2 mins. On the sixth attempt, your
	  access request will be denied.
	- Search for things in the directory. Register if there is not a single thing registered.
	- Now click on Request button for 5 times consecutively within 2 mins. On the sixth attempt your access request
	  should be denied
	- Wait for 2 mins to elapse, click on the request button again, you should be access the details of the thing once again.

## Aggregate query inside a GeoPolygon

This Feature lets you query for all the things that is present inside a geographical region (geopolygon). Following are the
sequence of steps to follow to test the feature.
1) Open the folder AggregatePolygonQuery\td. You will see a list of files of thing profiles.
2) Register the file TDBus1 to Level1 and continue as follows.
	- TDBus1 -> Level1
	- TDBus2a -> Level2a
	- TDBus2b -> Level2b
	- TDBus3aa -> Level3aa
	- TDBus3bb -> Level3bb
	- TDBus4aba -> Level4abb
	- TDBus5abba -> Level5abba
	- TDBus5abbb -> Level5abbb
Note that you need to run all. Navigate in the browser to appropriate level and then register.
3) Open config.py file, you will find that there is a configuration class for each level.
	For example : Level1 has a configuration class Level1DevConfig.
4) Each level's configuration class also has a member 'BOUNDING_BOX_COORDS'. This again represents a polygon
	that represents the level's bounding box. You can manipulate the coordinates to alter a level's bounding box.
	For the time being let it be as it is.
5) To visualise the level's bounding boxes as well as the things that you have registered. Follow the steps below.
	-  Navigate to http://geojson.io/
	-  Copy the contents of the file 'AggregatePolygonQuery/GeoJsonBoundingBoxWithThings.txt' and paste it in the JSON text box
	-  You should be able to see different polygons and each point represents a thing that we have registered in Step 2
6) Open 'AggregatePolygonQuery/GeoJsonBoundingBoxWithThings.png' image to see exactly the level and its bounding box marked.
7) Now copy the contents of the file 'AggregatePolygonQuery/GeoJsonBoundingBoxWithThingsAndInputPolygon.txt' and paste it in the JSON text box.
8) The only difference between this file and the previous file is that the current file has an additional polygon that intersects with three levels
    and encloses three things inside the polygon. The coordinates of this polygon is the last polygon in the file.
9) Copy the coordinates of the last polygon.
10) Navigate to any directory. (Example : http://localhost:5002/) and do the following steps.
	- Navigate to Custom script tab.
	- Locate the polygon key.
	- Paste the set of coordinates from step 9 and click on search
11) You should be able to see a count of two as this input polygon encloses two things.
12) You can repeat this step with any directory and any polygon with input polygon ranging from enclosing zero things
	to all the things that you have registered in step 2 and you should see the appropriate count.

