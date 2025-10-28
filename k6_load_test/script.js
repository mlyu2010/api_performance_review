import http from 'k6/http';
import { sleep } from 'k6';

export const options = {
    vus: 100,  // simulate 100 users
    iterations: 5000,  // total 10000 requests
};

// k6 main function
// A valid JWT token should be used after /login for Java Spring Boot (or /api/login for Python) endpoint returned it.

/*
For python endpoints
*/
export default function () {
    const port = 8000;
    const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc2MTY2NTEwM30.cMmcyJw8Ucr_oOYTlIMo9vczgvHHGKPoEqZnNcE6gv8';

    const params = {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
    };

    http.get(`http://localhost:${port}/api/tasks`, params);  // send GET request to /api/tasks with auth
    sleep(1);  // wait 1 sec between requests
}

/*
For java spring boot endpoints
export default function () {
    const port = 8080;
    const token = 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbiIsImlhdCI6MTc2MTYwMjE0MCwiZXhwIjoxNzYxNjg4NTQwfQ.c8wHQhnuvO4Izw25C8W6SPy-ctk09w5QDXr7JB80BWk';

    const params = {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
    };

    http.get(`http://localhost:${port}/tasks`, params);  // send GET request to /tasks with auth
    sleep(1);  // wait 1 sec between requests
}
*/

