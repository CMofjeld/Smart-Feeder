import React, {useState, useEffect, useCallback} from 'react';
import PropTypes from 'prop-types';
import ApiHelper from '../helpers/ApiHelper';
import { ProgressBar, Modal } from 'react-bootstrap';

const FoodLevelDisplay = props => {
    // Food level updating
    const [foodLevel, setFoodLevel] = useState(1.0);
    const [alertShown, setAlertShown] = useState(false);
    const [showModal, setShowModal] = useState(false);

    const handleCloseModal = () => setShowModal(false);

    const updateFoodLevel = useCallback(async () => {
        const apiHelper = new ApiHelper(props.token);
        let getUrl = props.apiBaseUrl + "/devices/" + props.deviceID + "/foodLevel";
        let levelResponse = 1.0;
        try {
            const result = await apiHelper.callApi(getUrl);
            const resultResponse = await result.json();
            levelResponse = resultResponse.foodLevel;
        } catch (e) {
            console.log(e);
        }
        finally {
            setFoodLevel(levelResponse);
            // Handle modal logic
            if (levelResponse < 0.1) { // Food is low
                if (!alertShown) {
                    setShowModal(true);
                    setAlertShown(true);
                }
            } else { // Food level is OK
                setShowModal(false);
                setAlertShown(false);
            }
        }
    }, [props.deviceID, props.token, alertShown, props.apiBaseUrl]);

    useEffect(() => {
        const interval = setInterval(async () => updateFoodLevel(), 5000);
        return () => {
          clearInterval(interval);
        };
      }, [updateFoodLevel]);

    return (
        <div className="foodLevelDisplay">
            <h3>Food Level</h3>
            <ProgressBar now={foodLevel * 100} label={`${parseInt(foodLevel * 100)}%`} />
            <Modal show={showModal} onHide={handleCloseModal}>
                <Modal.Header closeButton>
                    <Modal.Title>Low food alert</Modal.Title>
                </Modal.Header>
                <Modal.Body>Warning, feeder food level is at {`${parseInt(foodLevel * 100)}%`}</Modal.Body>
            </Modal>
        </div>
    )
};

FoodLevelDisplay.propTypes = {
    token: PropTypes.string.isRequired,
    deviceID: PropTypes.string.isRequired,
    apiBaseUrl: PropTypes.string.isRequired
};

export default FoodLevelDisplay;