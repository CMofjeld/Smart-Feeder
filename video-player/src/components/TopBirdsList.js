import React, { useCallback, useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import ApiHelper from '../helpers/ApiHelper';
import { Button, ListGroup, ListGroupItem } from 'react-bootstrap';

const TopBirdsList = props => {
    const [topBirds, setTopBirds] = useState([]);

    const updateTopBirds = useCallback(async () => {
        const apiHelper = new ApiHelper(props.token);
        let getUrl = props.apiBaseUrl + "/visits/topSpecies?limit=5";
        let topBirdsResponse = [];
        try {
            const result = await apiHelper.callApi(getUrl);
            const resultResponse = await result.json();
            topBirdsResponse = resultResponse.topSpecies;
        } catch (e) {
            console.log(e);
        }
        finally {
            setTopBirds(topBirdsResponse);
        }
    }, [props.apiBaseUrl, props.token]);

    useEffect(updateTopBirds, [updateTopBirds]);

    return (
        <div className="visitList">
            <h3>Top Visiting Birds:</h3>
            <ListGroup>
                {topBirds.map(bird => (
                    <ListGroupItem>{bird.common_name} : {bird.num_visits}</ListGroupItem>
                ))}
            </ListGroup>
            <Button variant="primary" onClick={updateTopBirds}>Refresh</Button>
        </div>
    );
};

TopBirdsList.propTypes = {
    token: PropTypes.string.isRequired,
    apiBaseUrl: PropTypes.string.isRequired
};

export default TopBirdsList;