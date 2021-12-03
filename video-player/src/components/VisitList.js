import React, { useCallback, useEffect, useRef, useState } from 'react';
import PropTypes from 'prop-types';
import { ListGroup, ListGroupItem } from 'react-bootstrap';

const VisitList = props => {
    const [visits, setVisits] = useState([]);
    const ws = useRef(null);

    const addVisit = useCallback((newVisit) => {
      if (visits.length > 4) {
        setVisits(visits.slice(0, -1));
      }
      setVisits(arr => [newVisit, ...arr]);
    }, [visits]);

    // Connect to websocket only when URL or Device ID change
    useEffect(() => {
        // Connect
        let webSocketUrl = `${props.webSocketBaseUrl}/${props.deviceID}`;
        console.log(`Web socket URL: ${webSocketUrl}`)
        ws.current = new WebSocket(webSocketUrl);

        // Set listeners
        ws.current.onopen = (event) => console.log(event.data);
        ws.current.onerror = (event) => console.error(event.data);
        ws.current.onclose = (event) => console.log(event.data);

        // Cleanup
        const wsCurrent = ws.current;
        return () => {
            wsCurrent.close();
        };
    }, [props.webSocketBaseUrl, props.deviceID]);

    // Listen for new messages on the websocket and update visit list
    useEffect(() => {
        if (!ws.current) return;

        ws.current.onmessage = (event) => {
            console.log(event.data);
            try {
              var eventJSON = JSON.parse(event.data);
              if ("visiting_bird" in eventJSON) {
                var visitString = `${eventJSON["visiting_bird"]} visited at ${eventJSON["visited_at"]}`;
                addVisit(visitString);
              }
            } catch (error) {
              console.error(error);
            }
        };
    }, [addVisit]);

    return (
        <div className="visitList">
            <h3>Visit Feed</h3>
            <ListGroup>
                {visits.map(visit => (
                    <ListGroupItem>{visit}</ListGroupItem>
                ))}
            </ListGroup>
        </div>
    );
};

VisitList.propTypes = {
    webSocketBaseUrl: PropTypes.string.isRequired,
    deviceID: PropTypes.string.isRequired
};

export default VisitList;