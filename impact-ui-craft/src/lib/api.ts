import axios from "axios";
import { AXIOS_STATUS, SERVICE_URL } from "../constants/config";

const API_URL = import.meta.env.VITE_BACKEND_URL;
const axiosInstance = axios.create({
    baseURL: API_URL,
    headers: {
        "Content-Type": "application/json",
        Authorization:
            sessionStorage.getItem("accessToken") ??
            sessionStorage.getItem("refreshToken") ??
            "",
    },
});
const onGoingRequest = {};
// stores data of ongoing request
// tag : Abort Controller

axiosInstance.interceptors.request.use(
    function (config) {
        // aborting on going request
        if (onGoingRequest[config.tag]) {
            onGoingRequest[config.tag]?.abort("Duplicate Request");
            delete onGoingRequest[config.tag];
        }

        if (config.tag) {
            onGoingRequest[config.tag] = config.controller;
            config.signal = config.signal;
        }

        if (config.TYPE.params) {
            config.params = config.TYPE.params;
        } else if (config.TYPE.query) {
            config.url = config.url + "/" + config.TYPE.query;
        }
        return config;
    },
    function (error) {
        return Promise.reject(error);
    }
);

axiosInstance.interceptors.response.use(
    function (response) {
        // serve when status code is 2xx
        return processResponse(response);
    },
    function (error) {
        // serve when status code is out of 2xx
        return processError(error);
    }
);

//******************************* */
//if success turns out to be true then return {isSuccess : true, data:Object}
//if failure is there  then return {isFailure : true, status: string, msg: string, code : int}
//******************************* */
const processResponse = (response) => {
    return response.data;
};
const processError = (error) => {
    if (error.response) {
        //request successfully made and server responded with status other then 200
        //that falls out of the range 2.x.x
        // console.log(`Error in response: `, error.toJSON());
        // return {
        //  isError: true,
        //  // msg: API_NOTIFICATION_MESSAGES.responseFailure,
        //  code: error.response.status,
        // };
        return { isError: true, code: "", ...error.response.data };
    } else if (error.request) {
        //request made but no response received
        console.log(`Error in request: `, error.toJSON());
        return {
            isError: true,
            message: AXIOS_STATUS[error.code]?.description,
            code: error.code,
        };
    } else {
        //something happened on frontend side
        console.log(`Error in Network: `, error.toJSON());
        return {
            isError: true,
            message: AXIOS_STATUS[error.code]?.description,
            code: error.code,
        };
    }
};

const getType = (value, body) => {
    if (value.params) {
        return { params: body };
    } else if (value.query) {
        if (typeof body === "object") {
            return { query: body._id };
        } else {
            return { query: body };
        }
    }
    return {};
};

const API = {};

for (const [key, value] of Object.entries(SERVICE_URL)) {
    API[key] = (body, showUploadProgress, showDownloadProgress) => {
        const controller = new AbortController();

        return axiosInstance({
            method: value.method,
            url: value.url,
            signal: controller.signal,
            tag: value.tag ?? "",
            data: value.method === "DELETE" ? {} : body,
            responseType: value.responseType,
            TYPE: getType(value, body),
            onUploadProgress: function (progressEvent) {
                if (showUploadProgress) {
                    let percentageCompleted = Math.round(
                        (progressEvent.loaded * 100) / progressEvent.total
                    );
                    showUploadProgress(percentageCompleted);
                }
            },
            onDownloadProgress: function (progressEvent) {
                if (showDownloadProgress) {
                    let percentageCompleted = Math.round(
                        (progressEvent.loaded * 100) / progressEvent.total
                    );
                    showDownloadProgress(percentageCompleted);
                }
            },
        });
    };
}

export { API };
