interface ServiceUrl {
    url: string;
    method: "GET" | "POST" | "PUT" | "DELETE";
    query?: boolean;
    tag?: string;
    params?: boolean;
    responseType?: string;
}

export const SERVICE_URL: Record<string, ServiceUrl> = {
    sendPrompt: {
        url: "/chat/stream",
        method: "POST",
        tag: "sendPrompt",
        params: true,
    },
    // getAllProducts: { url: "/getproducts", method: "GET", tag: "loadProducts" },
    // getCategories: { url: "/getCategories", method: "GET", query: true, tag: "category" },
};

export const AXIOS_STATUS = {
    ERR_NETWORK: {
        title: "Network Error",
        description:
            "Seems like you are not connected to network, Please connect to network",
    },
    ERR_CANCELED: {
        title: "Request Cancelled",
        description: "Request is Cancelled by the Client",
    },
    ERR_BAD_OPTION_VALUE: {},
    ERR_BAD_OPTION: {},
    ECONNABORTED: {},
    ETIMEDOUT: {},
    ERR_FR_TOO_MANY_REDIRECTS: {},
    ERR_DEPRECATED: {},
    ERR_BAD_RESPONSE: {},
    ERR_BAD_REQUEST: {},
    ERR_NOT_SUPPORT: {},
    ERR_INVALID_URL: {},
};
