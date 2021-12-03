import React from 'react';
import PropTypes from 'prop-types';
import TopBirdsList from './TopBirdsList';

const StatsTab = props => {

    return (
        <div>
            <TopBirdsList apiBaseUrl={props.apiBaseUrl} token={props.token}/>
        </div>
    );
};

StatsTab.propTypes = {
    token: PropTypes.string.isRequired,
    apiBaseUrl: PropTypes.string.isRequired
};

export default StatsTab;