import React from 'react';
import PropTypes from 'prop-types';
import UnwelcomeVisitorsToggle from './UnwelcomeVisitorsToggle';

const SettingsTab = props => {

    return (
        <div>
            <UnwelcomeVisitorsToggle deviceID={props.deviceID} token={props.token} apiBaseUrl={props.apiBaseUrl} />
        </div>
    );
};

SettingsTab.propTypes = {
    token: PropTypes.string.isRequired,
    apiBaseUrl: PropTypes.string.isRequired,
    deviceID: PropTypes.string.isRequired
};

export default SettingsTab;