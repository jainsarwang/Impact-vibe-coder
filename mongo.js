import mongoose from "mongoose"
import {databse_name} from "imoport_path_of_db"
import { version } from "react"
const org_model = new mongoose.schema({
    id:{
        type: Number,
        default:0,
    },
    name:{
        type: String,
        default:""
    }
},{
versionKey: false,
timestamps: true
})

const org_ssdmodel = mongoose.("contanct,", org_model)
export default org_ssdmodel

