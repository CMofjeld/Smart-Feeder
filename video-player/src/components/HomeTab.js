import React from 'react';
import PropTypes from 'prop-types';
import VisitList from './VisitList';
import FoodLevelDisplay from './FoodLevelDisplay';

const HomeTab = props => {

    return (
        <div>
            <FoodLevelDisplay deviceID={props.deviceID} token={props.token} apiBaseUrl={props.apiBaseUrl} />
            <VisitList webSocketBaseUrl={props.webSocketBaseUrl} deviceID={props.deviceID}/>
        </div>
    );
};

HomeTab.propTypes = {
    token: PropTypes.string.isRequired,
    deviceID: PropTypes.string.isRequired,
    apiBaseUrl: PropTypes.string.isRequired,
    webSocketBaseUrl: PropTypes.string.isRequired
};

export default HomeTab;