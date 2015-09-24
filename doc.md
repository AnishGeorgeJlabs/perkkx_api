# The Essentials
- All Api's return JSON data
- Almost every json result has the format 
```JSON
{ 
  success: <0 or 1>, 
  data: <The actual data if success is 1>, 
  error: <Only if some exception or error occurres> 
}```
- The base URL for all api's is `http://api.jlabs.co/perkkx/`. The rest of the documentation assumes this base url and will provide
the rest of the partial urls.

# Signup and Login
## Login
POST: `{ email: <The user email>, regID: <The registration id of the device> }`
URL: `/check`
Result: ```JSON
{
  success: 1
  userID: <The unique user id for the client. A six character word, containing 2 alphabets and 4 numerals>,
  name: <Complete user name, 'firstname lastname'>,
  email: <The same as the one which was sent>,
  cname: <The corporate's name, if corporate info is not present, then will be blank>
}
```