import React, {useCallback, useEffect, useState} from 'react';
import PropTypes from 'prop-types';
import { Form } from 'react-bootstrap';
import ApiHelper from '../helpers/ApiHelper';

const UnwelcomeVisitorsToggle = props => {
    const [unwelcomeVisitors, setUnwelcomeVisitors] = useState({
        "bear": true,
        "cat": true,
        "dog": true,
    });

    const constructUnwelcomeList = useCallback(() => {
        let unwelcomeList = []
        Object.entries(unwelcomeVisitors).forEach(([key, value]) => {
            if (value) unwelcomeList.push(key);
        });
        return unwelcomeList;
    }, [unwelcomeVisitors]);

    const checkUnwelcomeList = () => {
        const list = constructUnwelcomeList();
        console.log(list);
    };

    const sendUpdateToAPI = async () => {
        const postUrl = `${props.apiBaseUrl}/devices/${props.deviceID}/unwelcomeVisitors`;
        const unwelcomeList = constructUnwelcomeList();
        const body = JSON.stringify({"unwelcomeVisitors": unwelcomeList});
        const apiHelper = new ApiHelper(props.token);
        await apiHelper.callApi(postUrl, 'POST', {body: body});
    };

    const handleChange = async e => {
        setUnwelcomeVisitors(prevState => ({
            ...prevState,
            [e.target.name]: !prevState[e.target.name]
        }));
        await sendUpdateToAPI();
    };

    return (
        <div>
            <h3>Unwelcome Visitors:</h3>
            <Form>
            {
                Object.entries(unwelcomeVisitors).map( ([key, value]) => 
                    <Form.Check 
                        type="switch"
                        label={key}
                        id={`${key}-switch`}
                        name={key}
                        checked={value}
                        onChange={handleChange}
                    />
                )
            }
            </Form>
        </div>
    );
};

UnwelcomeVisitorsToggle.propTypes = {
    token: PropTypes.string.isRequired,
    apiBaseUrl: PropTypes.string.isRequired,
    deviceID: PropTypes.string.isRequired
};

export default UnwelcomeVisitorsToggle;