import axios, {
    AxiosInstance,
    AxiosResponse,
    AxiosProgressEvent,
    InternalAxiosRequestConfig,
    AxiosError,
    ResponseType,
    AxiosRequestConfig,
} from "axios";
import { AXIOS_STATUS, SERVICE_URL } from "@/constants/ivc/config";

interface CustomAxiosRequestConfig extends InternalAxiosRequestConfig {
    tag?: string;
    controller?: AbortController;
    TYPE?: {
        params?: any;
        query?: any;
    };
}

interface OngoingRequestMap {
    [key: string]: AbortController;
}

interface ApiResponse<T = any> {
    isError?: boolean;
    isSuccess?: boolean;
    data?: T;
    message?: string;
    code?: string | number;
}

interface AxiosStatusEntry {
    title?: string;
    description?: string;
}

type AxiosStatusType = {
    [key: string]: AxiosStatusEntry;
};

const API_URL = process.env.NEXT_PUBLIC_BACKEND_URL;
const axiosInstance: AxiosInstance = axios.create({
    baseURL: API_URL,
    headers: {
        "Content-Type": "application/json",
        Authorization:
            sessionStorage.getItem("accessToken") ??
            sessionStorage.getItem("refreshToken") ??
            "",
    },
});

const onGoingRequest: OngoingRequestMap = {};
// stores data of ongoing request
// tag : Abort Controller

axiosInstance.interceptors.request.use(
    function (config: CustomAxiosRequestConfig) {
        // aborting on going request
        if (config.tag && onGoingRequest[config.tag]) {
            onGoingRequest[config.tag]?.abort("Duplicate Request");
            delete onGoingRequest[config.tag];
        }

        if (config.tag && config.controller) {
            onGoingRequest[config.tag] = config.controller;
            config.signal = config.controller.signal;
        }

        if (config.TYPE?.params) {
            config.params = config.TYPE.params;
        } else if (config.TYPE?.query) {
            config.url = `${config.url}/${config.TYPE.query}`;
        }
        return config;
    },
    function (error: AxiosError) {
        return Promise.reject(error);
    }
);

axiosInstance.interceptors.response.use(
    function (response: AxiosResponse) {
        // serve when status code is 2xx
        return response;
    },
    function (error: AxiosError) {
        // serve when status code is out of 2xx
        return Promise.reject(error);
    }
);

//******************************* */
//if success turns out to be true then return {isSuccess : true, data:Object}
//if failure is there  then return {isFailure : true, status: string, msg: string, code : int}
//******************************* */
const processResponse = (response: AxiosResponse): ApiResponse => {
    return response.data;
};

const processError = (error: AxiosError): ApiResponse => {
    if (error.response) {
        //request successfully made and server responded with status other then 200
        //that falls out of the range 2.x.x
        const errorData = error.response.data as Record<string, unknown>;
        return {
            isError: true,
            code: "",
            ...errorData,
        };
    } else if (error.request) {
        //request made but no response received
        console.log(`Error in request: `, error.toJSON());
        const errorCode = error.code || "";
        const status = (AXIOS_STATUS as AxiosStatusType)[errorCode];
        return {
            isError: true,
            message: status?.description || "Unknown error",
            code: error.code,
        };
    } else {
        //something happened on frontend side
        console.log(`Error in Network: `, error.toJSON());
        const errorCode = error.code || "";
        const status = (AXIOS_STATUS as AxiosStatusType)[errorCode];
        return {
            isError: true,
            message: status?.description || "Unknown error",
            code: error.code,
        };
    }
};

interface TypeConfig {
    params?: boolean;
    query?: boolean;
}

const getType = (value: TypeConfig, body: any) => {
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

const API: Record<string, Function> = {};

for (const [key, value] of Object.entries(SERVICE_URL)) {
    API[key] = (
        body?: any,
        showUploadProgress?: (percentage: number) => void,
        showDownloadProgress?: (percentage: number) => void
    ) => {
        const controller = new AbortController();

        const config: AxiosRequestConfig = {
            method: value.method,
            url: value.url,
            signal: controller.signal,
            data: value.method === "DELETE" ? {} : body,
            responseType: (value.responseType as ResponseType) || undefined,
            onUploadProgress: function (progressEvent: AxiosProgressEvent) {
                if (showUploadProgress && progressEvent.total) {
                    let percentageCompleted = Math.round(
                        (progressEvent.loaded * 100) / progressEvent.total
                    );
                    showUploadProgress(percentageCompleted);
                }
            },
            onDownloadProgress: function (progressEvent: AxiosProgressEvent) {
                if (showDownloadProgress && progressEvent.total) {
                    let percentageCompleted = Math.round(
                        (progressEvent.loaded * 100) / progressEvent.total
                    );
                    showDownloadProgress(percentageCompleted);
                }
            },
        };

        // Add custom properties
        (config as CustomAxiosRequestConfig).tag = value.tag ?? "";
        (config as CustomAxiosRequestConfig).controller = controller;
        (config as CustomAxiosRequestConfig).TYPE = getType(value, body);

        return axiosInstance(config).then(processResponse);
    };
}

export { API };
