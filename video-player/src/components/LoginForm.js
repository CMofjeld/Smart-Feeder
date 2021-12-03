import React, {useState} from 'react';
import PropTypes from 'prop-types';
import { Form, Button } from 'react-bootstrap';

const LoginForm = props => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");

    const loginUser = async () => {
        var body = new URLSearchParams({
            'username': username,
            'password': password,
        });
        let loginUrl = props.apiBaseUrl + '/token';
        let token = null;
        token = await fetch(loginUrl, {
            method: 'POST',
            body: body
        })
            .then(data => {
                if (data.status === 401)
                    alert("Invalid username or password.");
                return data.json();
            })
            .catch(e => {
                console.log(e);
                return null;
            });
        return token;
    };

    const handleSubmit = async e => {
        e.preventDefault()
        const token = await loginUser();
        console.log(token);
        if (token && token.access_token) {
            props.setToken(token.access_token);
            props.setUsername(username);
        }
    };

    return (
        <div>
            <Form onSubmit={handleSubmit}>
                <Form.Group className="mb-3" controlId="formBasicUsername">
                    <Form.Label>Username</Form.Label>
                    <Form.Control
                        autoFocus
                        type="text"
                        placeholder="Enter username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                    />
                </Form.Group>

                <Form.Group className="mb-3" controlId="formBasicPassword">
                    <Form.Label>Password</Form.Label>
                    <Form.Control
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />
                </Form.Group>
                <Button variant="primary" type="submit">
                    Submit
                </Button>
            </Form>
        </div>
    );
};

LoginForm.propTypes = {
    apiBaseUrl: PropTypes.string.isRequired,
    setToken: PropTypes.func.isRequired,
    setUsername: PropTypes.func.isRequired
};

export default LoginForm;