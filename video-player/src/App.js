import './App.css';
import VideoPlayer from './components/VideoPlayer';
import HomeTab from './components/HomeTab';
import StatsTab from './components/StatsTab';
import LoginForm from './components/LoginForm';
import ApiHelper from './helpers/ApiHelper';
import SettingsTab from './components/SettingsTab';
import { Tab, Row, Nav, Col } from 'react-bootstrap';
import { useCallback, useEffect, useState } from 'react';

function App() {
  const TOKEN = process.env.REACT_APP_TOKEN;
  const CLIENT_API_ENDPOINT_URL = process.env.REACT_APP_CLIENT_API_ENDOINT_URL;
  const BACKEND_API_BASE_URL = process.env.REACT_APP_BACKEND_API_BASE_URL;
  const WEBSOCKET_BASE_URL = process.env.REACT_APP_WEBSOCKET_BASE_URL;

  const [apiToken, setApiToken] = useState();
  const [username, setUsername] = useState();
  const [deviceID, setDeviceID] = useState();

  const getDeviceID = useCallback(async () => {
    if (apiToken && username) {
      const apiHelper = new ApiHelper(apiToken);
      let getUrl = `${BACKEND_API_BASE_URL}/users/${username}`;
      try {
          const result = await apiHelper.callApi(getUrl);
          const resultResponse = await result.json();
          setDeviceID(resultResponse.devices[0].device_name);
      } catch (e) {
          console.log(e);
      }
    }
  }, [apiToken, username]);

  useEffect(getDeviceID, [getDeviceID]);

  if (!apiToken || !username || !deviceID) {
    return (
      <div className="page_content">
        <LoginForm apiBaseUrl={BACKEND_API_BASE_URL} setToken={setApiToken} setUsername={setUsername} />
      </div>
    )
  }
  return (
    <div className="page_content">
      <h1>Smart Feeder</h1>
      <Tab.Container id="left-tabs-example" defaultActiveKey="first">
        <Row>
          <Col sm={2}>
            <Nav variant="pills" className="flex-column">
              <Nav.Item>
                <Nav.Link eventKey="first">Home</Nav.Link>
              </Nav.Item>
              <Nav.Item>
                <Nav.Link eventKey="second">Video Player</Nav.Link>
              </Nav.Item>
              <Nav.Item>
                <Nav.Link eventKey="third">Stats</Nav.Link>
              </Nav.Item>
              <Nav.Item>
                <Nav.Link eventKey="fourth">Settings</Nav.Link>
              </Nav.Item>
            </Nav>
          </Col>
          <Col sm={10}>
            <Tab.Content>
              <Tab.Pane eventKey="first">
                <HomeTab deviceID={deviceID} token={apiToken} apiBaseUrl={BACKEND_API_BASE_URL} webSocketBaseUrl={WEBSOCKET_BASE_URL}/> 
              </Tab.Pane>
              <Tab.Pane eventKey="second">
                <VideoPlayer token={TOKEN} clientApi={CLIENT_API_ENDPOINT_URL} videoName="sample-cvr-video-sink" show={true}/> 
              </Tab.Pane>
              <Tab.Pane eventKey="third">
                <StatsTab token={apiToken} apiBaseUrl={BACKEND_API_BASE_URL} show={true}/> 
              </Tab.Pane>
              <Tab.Pane eventKey="fourth">
                <SettingsTab token={apiToken} apiBaseUrl={BACKEND_API_BASE_URL} deviceID={deviceID}/> 
              </Tab.Pane>
            </Tab.Content>
          </Col>
        </Row>
      </Tab.Container>
    </div>
  );
}

export default App;
